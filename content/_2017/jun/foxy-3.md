Title: Serwer proxy w Ruscie (część 3)
Date: 2017-06-04
Category: rust
Tags: rust, foxy
Summary: Model własności (ownership and borrowing), struktury, metody - szkielet echo serwera HTTP.

Kod dostępny [tutaj](https://github.com/kele/foxy/tree/part3).

## Obsługa protokołu HTTP
Rust ma w miarę dojrzałą bibliotekę do obsługi protokołu HTTP - jest nią
[**hyper**](https://github.com/hyperium/hyper). Biblioteka ta jest używana m.in.
przez [**Servo**](https://github.com/servo/servo), czyli prawdopodobnie
najpoważniejszy projekt pisany w Ruscie w tej chwili.

Jednak w ramach nauki, napiszę swój własny, prosty moduł do obsługi HTTP.

## Tworzenie nowego modułu
W Ruscie kod organizowany jest w paczkach (**crate**), a wewnątrz nich w
modułach. Paczki możemy porównać do bibliotek w innych językach. Każda paczka ma
swój główny moduł (**root module**), a jego potomkami mogą być inne moduły.

Aby użyć modułu, musimy go zadeklarować:

    ::rust
    mod http;

<a name="backref-1"></a>
Rust<sup>[1](#rust-i-cargo)</sup> wtedy będzie się spodziewać pliku `http.rs`
lub `http/mod.rs`. Tam też musimy zdefiniować nasz kod.

    ::rust
    // http/mod.rs
    pub struct HttpStream {

    }

Słowo kluczowe `struct` pozwala na zdefiniowanie nowej struktury, natomiast
`pub` oznacza tutaj, że chcemy, aby była ona widoczna na zewnątrz tego modułu
(odpowiednik `public` z C++ czy Javy).


## Projektowanie API i model własności
Skoro już wiemy, gdzie chcemy umieścić kod do obsługi protokołu HTTP, to nadszedł
czas na zaprojektowanie API.

Chciałbym, żeby głównym obiektem był `http::HttpStream`. Będzie on opakowaniem
dla `net::TcpStream` z dodatkiem specyficznych dla protokołu HTTP własności.
Będzie on też właścicielem połączenia TCP przez resztę działania programu.
Wydaje się, że to dobry moment na napisanie trochę o modelu własności Rusta.

## Model własności (**ownership, borrowing**)
Model własności jest prawdopodobnie najważniejszą cechą Rusta, wyróżniającą go
na tle współczesnych języków programowania.

W Ruscie, obiekt do funkcji możemy przekazać na trzy sposoby:

    ::rust
    let mut x = T{};

    foo(x);
    bar(&x);
    xyz(&mut x);

### `foo(x)`
W przypadku `foo`, `x` przekazywany jest przez **wartość**. W Ruscie oznacza to
jednak jedną z dwóch możliwości:

- `x` zostanie skopiowany (jeśli implementuje cechę `Copy`, o tym później), lub
- `x` zostanie **oddany na własność**.

W tym drugim przypadku, `x` nie będzie mógł być użyty po oddaniu go innej
funkcji! Przykładowo:

    ::rust
	struct X { }
	fn foo(x :X) { }

	fn main() {
		let x = X{};
		foo(x);
		foo(x);
	}

próba kompilacji powyższego kodu skończy się błędem:

	error[E0382]: use of moved value: `x`
	 --> <anon>:7:9
	  |
	  |     foo(x);
	  |         - value moved here
	  |     foo(x);
	  |         ^ value used here after move
	  |
	  = note: move occurs because `x` has type `X`, which does not implement the `Copy` trait

	error: aborting due to previous error

`x` zostaje tutaj **oddany na własność** funkcji `foo()`, co oznacza, że
tracimy do niego dostęp. Dzięki takiej semantyce, kompilator może zrobić dwie rzeczy:

- zabronić używania `x` po tym jak został oddany (jak oddasz komuś książkę, to
przecież nie możesz jej nadal czytać),
- poprawnie zdecydować, że to nie ta funkcja odpowiada za zwolnienie pamięci
(tylko `foo`, a być może inna funkcja, której `foo` przekazuje `x`).

W taki własnie sposób, Rust zapewnia bezpieczeństwo przy jednoczesnym braku
kosztu w trakcie wykonania programu (nie musimy zliczać referencji do `x`, ani
zaprzęgać do pracy garbage collectora).

### `bar(&x)`
`&x` w Ruscie oznacza, że zmienną **pożyczamy** (**borrowing**). Po skończonej
pracy, `bar()` musi oddać ją nam w nienaruszonym stanie. Tzn. przekazujemy `x`
tylko __do odczytu__.

Wtedy, bezpiecznie można wykonać kod taki jak:

	::rust
	bar(&x);
	bar(&x);

bo po każdym wywołaniu `bar(&x)`, `x` trafia z powrotem w nasze ręce.
Kompilator wie wtedy, że:

- `bar` nie musi się martwić o zwalnianie pamięci dla `x`,
- `bar` nie może trzymać `x` w nieskończoność (więcej o tym, jak długo `bar`
może korzystać z `x` opowiem przy okazji omawiania **lifetimes**).

### `xyz(&mut x)`
Podobnie jak `&x`, lecz tym razem pozwalamy zmieniać pożyczony obiekt. Dopiero
przy omawianiu **lifetimes** będzie można powiedzieć coś więcej o tym jak
różnie `&` oraz `&mut` są traktowane przez kompilator. Proszę o cierpliwość ;).

## Projektowanie API (ciąg dalszy)
Skoro wiemy już co nieco o tym jak przekazuje się zmienne w Ruscie, możemy
przejść do wymyślania, jak chcemy korzystać z naszego nowo utworzonego
`http::HttpStream`. Na początek, napiszemy sobie zwykły __echo server__, tzn.
będziemy odsyłać zapytania, które otrzymaliśmy.

	::rust
	// main.rs

	// ...

	mod http;

	fn handle_connection(tcp: net::TcpStream) {
		let mut h = http::HttpStream::new(tcp);

        // ... główna pętla znajdzie się tutaj ...
	}

Z pewnością potrzebujemy **oddać** połączenie TCP nowemu obiektowi `HttpStream`
(nie chcemy, aby ktokolwiek inny mógł pisać do tego samego gniazda) i posłuży
nam do tego funkcja `new`. W tej chwili, `HttpStream` będzie wyglądać tak:

	::rust
    // http/mod.rs

    use std::net;

	pub struct HttpStream {
		tcp: net::TcpStream,
	}

    impl HttpStream {
        pub fn new(tcp: net::TcpStream) -> HttpStream {
            HttpStream { tcp: tcp }
        }
    }

`impl` służy do implementowania metod dla danej struktury. Jak widać, zamiast
dodawać słowo kluczowe `pub` przed `impl`, robi się to na poziomie pojedynczych
metod. W tym przypadku, `new` jest **associated function** (w innych językach
nazwalibyśmy ją metodą statyczną (static method)), co oznacza, że nie potrzebuje
przyjmować obiektu tego typu jako swojego argumentu (ale dalej ma dostęp do
prywatnych pól). Stąd też wywołuje się ją jako `HttpStream::new()` zamiast
`h.new()`.

Jedynym zadaniem `new` jest przekazanie `tcp` do `HttpStream`. Robimy to, bo nie
chcemy, aby `tcp` było publicznym polem `HttpStream` (przynajmniej na razie).

	::rust
	// main.rs

	// ...

	mod http;

	fn handle_connection(tcp: net::TcpStream) {
		let mut h = http::HttpStream::new{tcp};

		while !h.is_closed() {
			let request = match h.get() {
				Ok(r) => r,
				Err(e) => {
					println!("Error while getting http request: {}", e);
					return;
				}
			};
            // ...
	}

Pojawiły się dwie nowe metody: `is_closed()` oraz `get()`.

    ::rust
    // http/mod.rs

    // ...

    use std::io;

    impl HttpStream {
        // ...

        pub fn get(&mut self) -> io::Result<HttpPacket> {
            // TODO
            Ok(HttpPacket {})
        }

        pub fn is_closed(&self) -> bool {
            // TODO
            false
        }
    }

`get` będzie służyć do odbierania pakietów HTTP (`HttpPacket`), w związku z tym:

- musi mieć możliwość zmiany pola `tcp`, stąd `get` przyjmuje mutowalną
  referencję (`&mut`) do obiektu typu `HttpStream` (`self`, podobnie jak w
  Pythonie),
- zwraca `io::Result<HttpPacket>`, bo tak [jak już
  wspominałem](serwer-proxy-w-ruscie-czesc-2.html), coś może podczas
  odczytywania pójść nie tak i chciałbym mieć możliwość obsługi błędu,
- na razie implementacja ogranicza się do zwrócenia `Ok(HttpPacket {})`, czyli
  pustego pakietu (gdybym chciał zwrócić błąd, użyłbym `Err` zamiast `Ok`).

`is_closed` natomiast, po prostu odpowiada na pytanie, czy połączenie zostało
zamknięte.

Jak widać, potrzebna jest nam nowa struktura, `HttpPacket`, która będzie
reprezentować pojedynczy pakiet HTTP.

    ::rust
    // http/mod.rs

    // ...

    pub struct HttpPacket {}


Pozostało teraz dopisać linijkę, odpowiadającą za odsyłanie odpowiedzi.

    ::rust
    // main.rs

    // ...

    fn handle_connection(tcp: net::TcpStream) {
        let mut h = http::HttpStream::new{tcp};

        while !h.is_closed() {
            let request = match h.get() {
                Ok(r) => r,
                Err(e) => {
                    println!("Error while getting http request: {}", e);
                    return;
                }
            };
            h.send(&http::HttpPacket{});
        }
    }

Oraz odpowiednią (pustą, na razie) implementację `send`:

    ::rust
    // http/mod.rs

    // ...

    impl HttpStream {
        // ...

        pub fn send(&mut self, packet: &HttpPacket) io::Result<()> {
            Ok(())
        }
    }

`send` może zwrócić błąd, ale poza tym, nie zwraca niczego interesującego. W
takim wypadku, przydaje się typ `()` (unit), podobny do `void` znanego z innych
języków.

## Podsumowanie
Jak widać, nie udało się napisać nam jeszcze niczego co jakkolwiek sensownie
działa, ale przebrnęliśmy przez kilka kluczowych cech Rusta, bez których
jakiekolwiek zrozumienie dowolnego kodu byłoby niemożliwe.

Mam nadzieję, ze w kolejnym poście uda mi się zaimplementować prosty serwer
echo.

# Pozostałe części
- [następny post (część 4)](serwer-proxy-w-ruscie-czesc-4.html)
- [poprzedni post (część 2)](serwer-proxy-w-ruscie-czesc-2.html)

<hr>

### Przypisy

<a name="rust-i-cargo"></a><sup>1</sup> W oficjalnej dokumentacji przez "Rust" rozumie się
zarówno sam język jak i `cargo`. ([wróć do tekstu](#backref-1))
