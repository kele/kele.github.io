Title: Serwer proxy w Ruscie (część 4)
Date: 2017-06-05
Category: rust
Tags: rust, foxy
Summary: Serwer echo (**lifetimes**, odbieranie i wysyłanie pakietów TCP)
lang: en
Status: draft

Kod dostępny [tutaj](https://github.com/kele/foxy/tree/part4).

## Projektowanie API - ciąg dalszy

### Stara definicja `HttpPacket`
W poprzednim poście naszkicowaliśmy API `HttpStream`, tak, że zawiera m.in.
metody `get` oraz `send`, które przyjmują bądź zwracają `HttpPacket`.

    ::rust
    pub struct HttpPacket {}

Tak wyglądała nasza robocza definicja `HttpPacket`. Ktokolwiek jednak miał do
czynienia z protokołem HTTP, wie jednak, że mozemy podzielić pakiety na
zapytania (request) i odpowiedzi (response).

#### Przykładowe zapytanie

    ::http
    GET /hello.htm HTTP/1.1
    User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
    Host: www.tutorialspoint.com
    Accept-Language: en-us
    Accept-Encoding: gzip, deflate
    Connection: Keep-Alive

#### Przykładowa odpowiedź

    ::http
    HTTP/1.1 200 OK
    Date: Mon, 27 Jul 2009 12:28:53 GMT
    Server: Apache/2.2.14 (Win32)
    Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT
    Content-Length: 88
    Content-Type: text/html
    Connection: Closed

    <html>
    <body>
    <h1>Hello, World!</h1>
    </body>
    </html>

### `get` -> `get_request`
W związku z powyższym, przemianujemy `get` na `get_request`.

### `HttpRequest` oraz `HttpResponse` zamiast `HttpPacket`
Na razie będziemy po prostu trzymać w nich jedynie `string::String`. Z czasem
będziemy dodawać do tych stuktur m.in. informacje o kodzie odpowiedzi, rodzaju
zapytania, wersji protokołu HTTP, URI i wiele innych rzeczy.

    ::rust
    // http/mod.rs
    // ...

    pub struct HttpRequest {
        pub data: string::String,
    }

    pub struct HttpResponse {
        pub data: string::String,
    }

### Implementacja `get_request`
Nagłówek pakietu HTTP zawsze kończy się dwoma znakami nowej linii, więc
chcielibyśmy mieć możliwość czytania z naszego gniazda bajt po bajcie, aż
napotkamy `"\n\n"`. Możemy do tego celu wykorzystać `std::io::Bytes`, który jest
iteratorem po pojedynczych bajtach dla typów mających cechę (trait)
`std::io::Read`.

Jak możemy przeczytać w dokumentacji, dla `std::net::TcpStream` zaimplementowano
cechę `Read`. Problem w tym, że gdybyśmy chcieli czytać z `TcpStream` bajt po
bajcie, musielibyśmy w kółko wywoływać metodę `read()`, która to najzwyczajniej
w świecie wykonywałaby wywołanie systemowe z prośbą o jeden bajt. Byłoby to
strasznie wolne. Na szczęście, nawet dokumentacja Rusta wspomina o tym problemie
i daje gotowe rozwiązanie: `std::io::BufReader`. Typ ten opakowuje coś co
spełnia `std::io::Read` i czyta z tego do wewnętrznego bufora, minimalizując w
ten sposób liczbę wywołań systemowych. My możemy wtedy, bez utraty wydajności,
czytać z `BufReader` bajt po bajcie.

Jak wspomniałem, `Bytes` jest iteratorem, więc aby wziąc z niego kolejny
element, korzystamy z metody `next()`.

    ::rust
    // http/mod.rs
    // ...

    pub fn get_request(&mut self) -> io::Result<HttpRequest> {
        // ...
        loop {
            let x = self.tcp_bytes.next().unwrap().unwrap() as char;
            // ...
        }
    }

`as char`, jak się można domyślić, służy po prostu do rzutowania na typ `char`
(podstawowy typ do reprezentacji znaku w Ruscie), w tym wypadku z `u8` (bajt).
Do czego służą `unwrap()`? Metoda ta jest zdefiniowana m.in. dla typów `Result`
oraz `Option`. `Result` może przechowywać `Ok` (wartość) lub `Err` (błąd),
natomiast `Option` może przechowayć `Some` (wartość) lub `None` (nic).
`unwrap()` dla obu tych typów ma takie same działanie, tzn.:

- jeśli obiekt reprezentuje wartość (`Ok` lub `Some`), zwróc ją (bez
  opakowania),
- jeśli jednak nie jest to poprawna wartość (czyli `Err` lub `None`),
  wykonaj `panic!` (na ogół rownoważne z zakończeniem działania programu).

W przypadku iteratora `Bytes`, `next()` zwraca `Option<Result<u8>>`. Jeśli nie
ma już więcej danych, zwrócone zostanie `None`, jeśli jednak otrzymaliśmy z
powrotem coś od wywołanego pod spodem `read()`, otrzymamy `Some(x)`, gdzie `x`
będzie odczytanym bajtem (`Ok(b)`) lub błędem (`Err(e)`). Stąd potrzebne są nam
dwa `unwrap()`'.

Pełna implementacja `get_request`:

    ::rust
	// http/mod.rs
	// ...

	pub fn get_request(&mut self) -> io::Result<HttpRequest> {
		// TODO: error handling
		let mut lastChar = '\0';
		let mut packet = string::String::new();

		loop {
			let x = self.tcp_bytes.next().unwrap().unwrap() as char;
			packet.push(x);
			if lastChar == '\n' && x == '\n' {
				break;
			}
			lastChar = x;
		}

		Ok(HttpRequest { data: packet })
	}

Na razie, w przypadku jakiegokolwiek błędu, będziemy poprostu kończyć pracę
programu (poprzez `unwrap()`).

### Dzielenie obiektów
W `get_request` korzystaliśmy z `self.tcp_bytes`. Wcześniej, `HttpStream`
składał się z `tcp` typu `net::TcpStream`. Teraz, będziemy mieć tam nowe pole,
typu `io::Bytes<io::BufReader<net::TcpStream>>` (iterator po bajtach odczytanych
z `TcpStream` z buforowaniem). Problem w tym, że taki typ bierze sobie
`TcpStream` na własność. A my, oprócz odbierania danych, chcielibyśmy także coś
wysyłać!

<a name="backref-1"></a>
W językach z garbage collectorem dzielenie obiektów jest całkiem łatwe. W
językach typu C++, możemy skorzystać z dobrodziejstw typu `std::shared_ptr` lub
referencji. Jakie problemy niosą za sobą te rozwiązania?

- garbage collector wiąże się ze spadkiem wydajności i marnymi gwarancjami co do
  tego, kiedy zasoby zostaną zwolnione,
- `std::shared_ptr` to zliczanie referencji, które też wiąże się z pewnym
  narzutem wpływającym na wydajność (poza tym, obiekt
  musi<sup>[1](#shared-ptr)</sup> być zaalokowany na stercie),
- referencje nie są bezpieczne ([**dangling reference**](https://en.wikipedia.org/wiki/Dangling_pointer)).

Rust jest nastawiony bardzo mocno na bezpieczeństwo (memory safety) oraz
wydajność. Oczywiście moglibyśmy zwyczajnie skorzystać ze zliczania referencji
`alloc::rc::Rc`, ale nie zyskalibyśmy wtedy zbyt wiele w stosunku do
`std::shared_ptr` znanego z C++.

<a name="backref-2"></a>
Skorzystamy więc z referencji. Jak mieć w języku referencje, a jednocześnie nie
pozwolić na możliwość zaistnienia wspomnianego wyżej problemu **dangling
reference**<sup>[2](#dangling-tlumaczenie)</sup>?

Możemy powiedzieć kompilatorowi, jak długo obiekty będą żyć!

### Lifetimes
    ::rust
    // http/mod.rs
    // ...

    pub struct HttpStream<'a> {
        tcp: &'a net::TcpStream,
        tcp_bytes: io::Bytes<io::BufReader<&'a net::TcpStream>>,
    }

    impl<'a> HttpStream<'a> {
        pub fn new(tcp: &'a net::TcpStream) -> HttpStream<'a> {
            HttpStream {
                tcp: tcp,
                tcp_bytes: io::BufReader::new(tcp).bytes(),
            }
        }

        // ...
    }

W Ruscie kiedykolwiek zobaczymy nazwę zaczynającą się od `'`, jak np `'a` lub
`'static`, będzie to oznaczenie lifetime'u. W przypadku powyższego kodu, mówimy
kompilatorowi, że:

- `HttpStream`, jako jeden z parametrów, przyjmuje lifetime (wewnątrz definicji
  `HttpStream` nazwiemy go `'a`),
- `tcp` jest referencją na obiekt `net::TcpStream` o lifetime `'a`,
- `tcp_bytes` jest iteratorem `Bytes` po buforowanym `Reader`, `Reader` ten jest
  referencją na obiekt typu `net::TcpStream` o lifetime `'a`.

Co zyskujemy dzięki temu, że dodaliśmy kilka `'a` tu i ówdzie? Kompilator wie,
że `tcp_bytes` będzie trzymać referencje na `net::TcpStream` tak długo jak robi
to struktura `HttpStream`, której jest częścią. Dzięku temu, `Bytes` oraz
`BufReader`, które składają się na `tcp_bytes`, **zawsze będą wskazywać na żywy
obiekt** `net::TcpStream`. Za kilka dodatkowych znaków ustrzegliśmy się przed
problemem dangling reference **w czasie kompilacji!** Bezpieczeństwo przy
zerowym koszcie wykonania, tego oczekiwaliśmy od Rusta.

Tak naprawdę to kiedykolwiek w Ruscie korzystamy z referencji, korzystamy także
z lifetimes. Tyle tylko, że często kompilator potrafi sam się domyślić, skąd
wziąc informację o tym jak długo obiekt będzie żył. Technika ta nazywa się
**lifetime elision**.

### `send()`
Implementacja `send()`, która ma po prostu wysłać jakieś dane (bez układania ich
w prawdziwy pakiet HTTP) jest trywialna:

    ::rust
    // http/mod.rs
    // ...

    pub fn send(&mut self, resp: &HttpResponse) -> io::Result<()> {
        // TODO: error handling
        self.tcp.write(resp.data.to_string().as_bytes());
        Ok(())
    }

### Zmiany w głównej pętli
Zmieniliśmy `HttpPacket` na `HttpResponse` i
`HttpRequest`. Oprócz tego, `HttpStream` przyjmuje teraz `net::TcpStream` przez
referencję (a nie na własność). W związku z tym nowa główna pętla wygląda teraz
tak:

    ::rust
    // main.rs
    // ...

    fn handle_connection(tcp: net::TcpStream) {
        let mut h = http::HttpStream::new(&tcp);

        while !h.is_closed() {
            let request = match h.get_request() {
                Ok(r) => r,
                Err(e) => {
                    println!("Error while getting http request: {}", e);
                    return;
                }
            };
            h.send(&http::HttpResponse { data: request.data.clone() });
        }
    }

`clone()` jest metodą, która kopiuje obiekt typu `string::String`. Jest to jedna
z metod typów, które implementują cechę `Clonable`.

## Podsumowanie
Udało się nam napisać proste funkcje `get_request()` oraz `send()`, co pozwala
na implementację serwera echo. Jak sprawdzić jego działanie? Można zrobić, np.:

    ::shell
    cat | netcat 127.0.0.1 4000

i zacząć pisać. Pamiętać trzeba, że tylko przy naciśnięciu klawisza enter dwa
razy z rzędu, nasz serwer wyśle odpowiedź.

W kolejnych częściach zajmiemy się obsługą błędów (`unwrap()` nie powinno
przejść code review w tym przypadku) oraz tym, co tak naprawdę znajduje się w
pakietach HTTP.


# Pozostałe części
- [następny post (część 5) (obsługa błędów)](serwer-proxy-w-ruscie-czesc-5.html)
- [poprzedni post (część 3)](serwer-proxy-w-ruscie-czesc-3.html)


### Przypisy

<a name="shared-ptr"></a><sup>1</sup> Możliwe jest, aby `shared_ptr` wskazywał
na obiekty na stosie, albo na zasoby zupełnie innego typu (np. pliki), ale żeby
zrobić to dobrze, potrzeba naprawdę solidnej wiedzy dotyczącej zaawansowanego
C++. Nawet wtedy, nie musi to być bezpiecznym rozwiązaniem.
([wróć do tekstu](#backref-1))

<a name="dangling-tlumaczenie"></a><sup>2</sup> Przykro mi, "wiszące referencje"
nie brzmi najlepiej.
([wróć do tekstu](#backref-1))
