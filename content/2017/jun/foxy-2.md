Title: Serwer proxy w Ruscie (część 2)
Date: 2017-06-03
Category: rust
Tags: rust, foxy
Summary: Początkowy szkielet programu.

## Posłuchajmy czegoś po TCP
Tak wygląda szkielet naszego programu (wyjaśnienia poniżej):

    ::rust
    // main.rs

    use std::net;

    const PROXY_PORT: u16 = 4000;

    fn main() {
        let listener = net::TcpListener::bind(("127.0.0.1", PROXY_PORT)).unwrap();

        match listener.accept() {
            Ok((sock, _)) => handle_connection(sock),
            Err(e) => panic!("Error while accepting connection: {}", e),
        }
    }

    fn handle_connection(tcp: net::TcpStream) {
        println!("Opened connection: {:?}", tcp)
    }

### Nasłuchiwanie
Używać będziemy paczki (__crate__)
[`std::net`](https://doc.rust-lang.org/std/net/). Robimy to za pomocą:

    ::rust
    use std::net;

Użyjemy funkcji
[`std::net::TcpListener::bind`](https://doc.rust-lang.org/std/net/struct.TcpListener.html),
żeby zacząć nasłuchiwać na porcie 4000 lokalnej maszyny:

    ::rust
    const PROXY_PORT: u16 = 4000;
    let listener = net::TcpListener::bind(("127.0.0.1", PROXY_PORT)).unwrap();

`u16` to odpowiednik `uint16`, zatem `const PROXY_PORT: u16 = 4000;` jest po
prostu deklaracją stałej `PROXY_PORT` typu liczba naturalnia 16-bitowa o
wartości 4000.

Czym jest tajemnicze `unwrap()` na końcu? Rust jest językiem nastawionym przede
wszystkim na bezpieczeństwo, wymuszane już w czasie kompilacji. Na czym to
dokładnie polega w tym przypadku? `bind()` mógłby zwyczajnie zwrócić
`TcpListener`, jednak zamiast tego zwraca
[`std::io::Result<TcpListener>`](https://doc.rust-lang.org/std/io/type.Result.html).

Co to za różnica?

Coś po drodze może pójść nie tak (np. port może być już zajęty). Można radzić sobie z tym na różne sposoby:

- rzucając wyjątek (Java, C++?),
- zwracając wskaźnik (C, C++),
- zwracając dwie wartości `(TcpListener, bool)` (Go),
- [`std::optional`](http://en.cppreference.com/w/cpp/utility/optional) (C++17).

Rzucenie wyjątku nie wymusza na programiście obsłużenia go. Zwracanie wskaźnika
czy wartości typu `bool` również. `std::optional` wystarczy ominąć prostym `*`.
Rust idzie jednak inną drogą. Zamiast powyższych rozwiązań, zwracane jest
opakowanie (`Result`), które może zawierać oczekiwaną przez nas
wartość `TcpListener` lub błąd (`Error`)!

W związku z tym, że rozpoczęcie
nasłuchiwania na jakimś porcie jest kluczowe dla działania programu, jedyne co
robię, to rozpakowuję wynik (`unwrap()`).

Cóż robi ta tajemnicza metoda? Jeśli nie było błędu - zwraca wartość. Jeśli
pojawił się błąd, wykonuje się
[`panic!`](https://doc.rust-lang.org/std/macro.panic.html) (odpowiednik
[`panic`](https://blog.golang.org/defer-panic-and-recover) z Go).

### Akceptowanie połączenia
    ::rust
    match listener.accept() {
        Ok((sock, _)) => handle_connection(sock),
        Err(e) => panic!("Error while accepting connection: {}", e),
    }

Jeśli udało się poprawnie zaakceptować połączenie, wywołajmy
`handle_connection(sock)`, które zajmie się dalszą obsługą połączenia.

Jeśli nie - `panic!` z odpowiednim komunikatem o błędzie.

### `match`
`match` jest konstrukcją, która jest spotykana raczej w językach funkcyjnych
(OCaml, Haskell, Lisp) niż w imperatywnych (C, Python, Java, C++), dlatego
chciałbym poświęcić jej parę zdań.

[**Pattern matching**](https://en.wikipedia.org/wiki/Pattern_matching), bo tak
nazywa się ta konstrukcja, służy do:

- sprawdzania, czy obiekt jest taki jak nam się wydaje (w powyższym przypadku,
  czy to jest `Ok` (prawidłowa wartość) czy `Err` (błąd)),
- rozłożenia go na mniejsze porcje (`Ok` w powyższym przykładzie składa się z
  dwóch cześci, pierwszą jest socket, drugą adres, adres ignoruję (poprzez `_`),
  ale socket zapamiętuję jako `sock`),

Przykładowo, gdbyśmy pisali kalkulator oparty na drzewach wyrażen
arytmetycznych, pewna częśc kodu mogłaby wyglądać tak:

    ::rust
    match expression {
        Add(x, y) -> x + y,
        Sub(x, y) -> x - y,
        Mul(x, y) -> x * y,
        Div(x, y) -> x / y,
    }

Taka konstrukcja w językach programowania jest możliwa dzięki istnieniu
specjalnych typów, które są alternatywą różnych wartości. Tzn. wyrażenie
arytmetyczne może być dodawaniem, odejmowaniem, mnożeniem lub dzieleniem.
Informacja o tym, czym właściwie jest dane wyrażenie, jest zapisywana i
sprawdzana w czasie wykonania programu. To co jest ważne, to fakt, że kompilator
wie, jakie są wszystkie możliwe alternatywy (i może nas ostrzec, gdy o którejś
zapomnimy!). W C++ możnaby to symulować w taki sposób:

    ::cpp
    enum Type { Add, Sub, Mul, Div };

    struct Expression {
        Type type;
        union {
            Add add;
            Sub sub;
            Mul mul;
            Div div;
        } expr;
    };

    switch expr.type {
        case Type::Add: return expr.add.x + expr.add.y; break;
        case Type::Sub: return expr.add.x - expr.add.y; break;
        case Type::Mul: return expr.add.x * expr.add.y; break;
        case Type::Div: return expr.add.x / expr.add.y; break;
    }

Jak widać, pattern matching jest dość wygodny. W językach, które go wspierają,
implementacja jest na ogół wydajniejsza niż to co pokazałem powyżej w C++.
Niestety, za mało jeszcze wiem o Ruscie, żeby wiedzieć jak wyglądają jego
wewnętrzne mechanizmy w tym wypadku.

### `panic!` oraz `{}`
`panic!` jest makrem (na razie możemy traktować to jako funkcję, lecz `!` jest w
Ruscie sygnałem, że w istocie jest to makro), które używane jest w przypadku
krytycznych dla działania programu błędów.

`panic!` przyjmuje argumenty podobne do `printf` znanego z wielu innych języków,
tyle tylko, że `{}` pozwala na wyświetlenie wartości dowolnego (no, nie do
końca, ale o tym kiedy indziej) typu.

## Co dalej?
W kolejnych postach planuję omówić:

- obsługę zapytań w różnych wątkach,
- semantykę własności i pożyczania (ownership and borrowing) (jest to główna
  cecha wyróżniająca Rust na tle innych popularnych języków programowania),
- tworzenie włąsnych struktur,
- metody,
- implementacje cech (trait),
- wyrażenia i rozkazy (expressions and statements),
- i wiele innych.

