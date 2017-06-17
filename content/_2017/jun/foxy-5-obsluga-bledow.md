Title: Serwer proxy w Ruscie (część 5)
Date: 2017-06-17
Category: rust
Tags: rust, foxy, error handling, macros
Summary: Obsługa błędów, makra.

## Błędy, błędy, wszędzie błędy
Dopóki pisze się małe skrypty dla własnego użytku, obsługa błędów nie jest tak
istotna. Kiedy tylko zaczyna się **(a)** pisać oprogramowanie dla innych,
**(b)** korzystać z wejścia/wyjścia (pliki, połączenia sieciowe, itd.), to nagle
okazuje się, że obsługa błędów zajmuje naprawdę dużo czasu programisty.

## Bez wyjątków
Jedną z technik jakie kiedyś wymyślono, żeby obsługa błędów była mniej
uciążliwa dla programisty jest mechanizm wyjątków (exceptions). Większość
popularnych języków (Java, C#, C++, Python) wspiera wyjątki.

Dwa największe problemy tego rozwiązania to:

- spadek wydajności,
- łatwo można zignorować obsługę wyjątku.

Pierwsza wada dotyczy zastosowań, w których **wydajność (lub minimalizowanie
opóźnień) gra kluczową rolę dla działania systemu**. Rust jest językiem, który
jest przeznaczony m.in. do takich zastosowań. Drugi problem byłby także dużą
skazą dla języka, który tak wiele robi aby oprogramowanie było bezpieczne.

### Go
Jednym ze współczesnych języków programowania, które nie wspierają mechanizmu
wyjątków jest Go. W tym przypadku, obsługa błędów wygląda mniej więcej jak w C.

    ::go
    if err := foo(); err != nil {
        return nil, err
    }

Powyższy kawałek kodu pojawia się naprawdę bardzo, bardzo często. Na tyle, że
możnaby pomyśleć o sprawieniu sobie takiej klawiatury specjalnie do pisania w
Go:

[![/r/ProgrammingHumor](http://i.imgur.com/EVc3Nm0.png
"/r/ProgrammingHumor")](https://www.reddit.com/r/ProgrammerHumor/comments/6fmlxj/introducing_the_go_keyboard/)

## Jak robi to Rust?
Rust ma nieco inne podejście. Przy pomocy swojego systemu typów, stara się
osiągnąć:

- trudną do zignorowania obsługę błędów,
- brak spadku wydajności spowodowanego obsługą wyjątków.


### `Option`, `Result`
Bazą są typy `Option` i `Result`, o których wspominałem już w poprzednich
postach. Pierwszy reprezentuje __coś albo nic__ (podobnie jak
[std::optional](http://en.cppreference.com/w/cpp/utility/optional) z C++), drugi
zaś __wartość albo błąd__. W obu przypadkach **albo** należy rozumieć jako
**dokładnie jedna z możliwości**.

    ::rust
    let x: Option<i32> = foo();
    match x {
        Some(n) => println!("Nasza liczba: {}", n),
        None => println!("Oops, coś poszło nie tak."),
    }

Jak można się domyślać, obiekty typu `Option` lub `Result` nie mogą być użyte
"wprost". Zawsze trzeba je jakoś odpakować. Najprościej można to zrobić przy
pomocy metody `unwrap()`:

    ::rust
    let x: Option<i32> = foo();
    println!("Nasza liczba: {}", x.unwrap());

Co się wtedy stanie? `unwrap()` zwróci wartość jeśli `Option` ją zawiera, a
jeśli nie, wywołane zostanie `panic!` (kończące pracę działania programu).
Oprócz `unwrap()` zaimplementowano też kilka innych, bardzo przydantych metod:

- `unwrap_or(v)` - odpakuj, a jeśli nic nie znajdziesz, zwróć `v`
- `unwrap_or_default()` - zwróć domyślną wartość, jeśli nic nie znajdziesz.

W związku z tym, wydaje się, że każde solidne narzędzie do code review dla Rusta
powinno podświetlać `unwrap()` na czerwono. :)

### `try!` oraz `?`

Jak widać, `Option` niezbyt ustrzega nas przed pisaniem kodu podobnego do tego w
Go. W tym może nam pomóc typ `Result`, który można użyć w ten sposób:

    ::rust
    let x: Result<i32, Error> = bar();

    match x {
        Ok(n) => println!("Nasza liczba: {}", n),
        Err(e) => return Err(e),
    }

Taka konstrukcja, jak można się domyślać, byłaby używana bardzo, bardzo często.
W związku z tym, można ją skrócić do:

    ::rust
    let x: Result<i32, Error> = bar();

    println!("Nasza liczba: {}", try!(x))

lub

    ::rust
    let x: Result<i32, Error> = bar();

    println!("Nasza liczba: {}", x?)

Ta druga forma jest szczególnie przydatna, kiedy chcemy coś odpakować z kilku
warstw. `?` jest jedynie lukrem syntaktycznym i jest równoważne użyciu `try!`.


## Kilka słów o makrach

Zarówno `try!` jak i `panic!`, `println!`, `write!` są makrami. Ich cechą
wspólną jest to, że ich wywołania zawierają w sobie `!`, w przeciwieństwie do
funkcji. Ze względu na bardzo rygorystyczny system typów Rusta, niektóre wzorce
trudno jest zapisać jako zwyczajne funkcje. Wtedy przychodzą z pomocą makra.

Makra, podobnie jak w C, są po prostu lukrem syntaktycznym i są zamieniane na
swoje ciało podczas kompilacji. W przeciwieństwie do C, makra w Ruscie są
bardziej zaawansowane i mniej podatne na nadużycia (np. nie da się zrobić
`#define true false`).

Na razie niewiele wiem o pisaniu makr, dlatego ograniczymy się do ich używania,
zamiast tworzyć nowe (prawdopodobnie zbędne).

## Wracamy do `try!`

Skoro wiemy już, że `try!` jest makrem, warto byłoby się dowiedzieć jak ono
działa.

*(...) In case of the Err variant, it retrieves the inner error. __try! then
performs conversion using From.__ This provides automatic conversion between
specialized errors and more general ones. The resulting error is then
immediately returned. (...)*
[rust-lang.org](https://doc.rust-lang.org/nightly/std/macro.try.html)

Rust unika niejawnych konwersji (np. między kawałkiem napisu `&str`
a obiektem, który jest napisem i właścicielem pamięci, w której się on znajduje
`String`). W związku z tym, pisząc kod często możemy się natknąć na to, że
funkcja, w której używamy `try!` zwraca inny typ błędu niż wartość, którą chcemy
odpakować. Wtedy przydaje się cecha `std::convert::From`:

    ::rust
    pub trait From<T> {
            fn from(T) -> Self;
    }

Oznacza ona po prostu tyle co: z obiektu `T` możemy zrobić obiekt `Self`.

Przykładowo, jeśli wynikiem działania naszej funkcji mógłby być `io::Error` (np.
zerwane połączenie TCP), lub `str::Utf8Error` (nie udało się poprawnie odczytać
napisu), to moglibyśmy napisać sobie taki kod:

    ::rust
	enum MyError {
		Utf8,
		Io(io::Error),
	}

	impl From<Utf8Error> for MyError {
		fn from(_: Utf8Error) -> Self {
			MyError::Utf8
		}
	}

	impl From<io::Error> for MyError {
		fn from(e: io::Error) -> Self {
			MyError::Io(e)
		}
	}

	fn utf8() -> Result<i32, Utf8Error> {
		Ok(1)
	}

	fn read() -> Result<i32, io::Error> {
		Ok(2)
	}

	fn foo() -> Result<i32, MyError> {
		let x = utf8()?;
		let y = read()?;
		Ok(x + y)
	}

Powiedzieliśmy w ten sposób kompilatorowi, w jaki sposób powinien przekształcać
jeden rodzaj błędów na inny. W tym przypadku zdecydowaliśmy, że nie interesują
nas szczegóły błędu `Utf8Error` w związku z tym zignorowaliśmy jego zawartość,
ale już `io::Error` jest dla nas interesujące. Oba typy błędów mogą znaleźć się
teraz w `MyError` i swobodnie można używać `?`.

Dopisanie implementacji cechy `From` wydaje się żmudną pracą, ale za te kilka
linijek dostajemy dużo większą kontrolę nad obsługą błędów, bez ryzyka
przypadkowych zupełnie konwersji.

## Podsumowanie
W tej części nie napisaliśmy żadnego kodu, który znajdzie się w
implementacji naszego serwera HTTP. Niemniej jednak, aby był on odporny na
różnego rodzaju problemy (chcę go używać cały czas), zrozumienie obsługi błędów
w Ruscie będzie kluczowe dla powodzenia tego projektu. :)

# Pozostałe części
- następny post (część 6) w przygotowaniu
- [poprzedni post (część 4)](serwer-proxy-w-ruscie-czesc-4.html)

