Title: Serwer proxy w Ruscie (część 6)
Date: 2017-06-18
Category: rust
Tags: rust, foxy, error handling, macros
Summary: Działający serwer echo! Parsowanie zapytań, własne cechy i wiele innych.
lang: pl

Kod dostępny [tutaj](https://github.com/kele/foxy/tree/part6).

## Nowa implementacja `HttpStream::get_request`

    ::rust
    // http/mod.rs

    pub fn get_request(&mut self) -> Result<Option<Request>> {
        let mut input = String::new();
        while !input.ends_with("\r\n\r\n") {
            let x = match self.tcp_bytes.next() {
                None => return Err(Error::new(ErrorKind::UnexpectedEof, "")),
                Some(r) => r? as char,
            };
            input.push(x);
        }

        let header = RequestHeader::parse(input.lines())?;
        let body = Vec::new(); // TODO: read the body

        Ok(Some(Request {
                    header: header,
                    body: body,
                }))
    }

### `ends_with()`
Pierwszą isostną zmianą jest użycie metody `ends_with()`, która sprawdza czy
napis kończy się danym wzorcem (w tym przypadku są to po prostu dwie sekwencje
CRLF, czyli nowe linie w kodowaniu DOS).

### `RequestHeader::parse()`
Zamiast zapisywać nagłówek w surowej formie, jest on teraz parsowany przez
funkcję `parse()`. Znak zapytania na końcu służy do odpakowania wartości i
ewentualnej propagacji błędu.

### Brak ciała
Na początek skupimy się na obsłudze zapytań `GET`, które zwykle nie mają ciała.

## Moduł `header`

Nagłówek żądania HTTP ma formę:

    ::http
    GET /hello.htm HTTP/1.1
    User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
    Host: www.tutorialspoint.com
    Accept-Language: en-us
    Accept-Encoding: gzip, deflate
    Connection: Keep-Alive

Składa się on z:

- jednej linii zawierającej rodzaj zapytania, URI oraz wersję protokołu,
- kolejnych linii formatu \<pole\>: \<wartość\>,
- "\r\n\r\n" (czyli dwa CRLF).

Do przetwarzania nagłówków utworzymy sobie nowy moduł `header` w pliku
`http/header.rs`.

Zawierać on będzie (podobne do siebie) definicje nagłówka żądania
`RequestHeader` oraz zapytania `ResponseHeader`.

    ::rust
    // http/header.rs

    pub struct RequestHeader {
        pub method: RequestMethod,
        pub uri: String,
        pub protocol: String,
        pub fields: HashMap<String, String>,
    }

`RequestMethod` będzie typem `enum` zawierającym możliwe typy żądań HTTP. Na
razie interesować nas będzie wyłącznie `GET`.

    ::rust
    #[derive (Clone, Copy)]
    pub enum RequestMethod {
        Get,
        // TODO: add more methods here
    }

Korzystamy z `enum`, ponieważ jest tylko kilka możliwych rodzajów zapytań HTTP i
chcielibyśmy móc o nich mówić bez każdorazego porównywania napisów "GET", "POST"
czy "CONNNECT". Drugim argumentem jest fakt, że w taki sposób pomagamy
kompilatorowi w wyłapywaniu błędów. Przykładowo, dla takiego kodu:

    ::rust
    pub enum Xyz {
        Foo,
        Bar,
        Baz,
    }

    fn code() -> Xyz {
        Xyz::Foo
    }

    fn main() {
        match code() {
            Xyz::Foo => println!("Foo"),
            Xyz::Bar => println!("Bar"),
            // Ups! Zapomnieliśmy o implementacji dla Baz!
        }
    }

otrzymalibyśmy następujący błąd kompilacji:

    ::shell
    error[E0004]: non-exhaustive patterns: `Baz` not covered
      --> <anon>:12:15
       |
    12 |         match code() {
       |               ^^^^^^ pattern `Baz` not covered

    error: aborting due to previous error

Dyrektywa `#[derive (Clone, Copy)]` jest tutaj instrukcją do kompilatora, ktora
każe mu zaimplementować cechy `Clone` i `Copy` (obie pozwalają na kopiowanie
obiektu, w nieco inny sposób, o tym kiedy indziej) dla typu `RequestMethod` na
podstawie jego składowych.  W tym przypadku, robimy to z dwóch powodów:

- wydaje się naturalnym, że taki typ powinien móc być łatwo kopiowany,
- chcemy później w łatwy sposób zaimplementować cechę `Clone` dla żądania
  `Request`, którego `RequestMethod` jest składową.

Dyrektywy `derive` są bardzo przydatne kiedy chcemy zaimplementować cechy, z
którymi spokojnie sobie poradzi kompilator (m.in. `Clone`, `Debug`). W tej
chwili nie wiem jeszcze jakie cechy można umieścić w tej dyrektywie, ale pewnie
niedługo się dowiem. :)

### Parsowanie nagłówka żądania HTTP
    ::rust
    // http/header.rs

    impl RequestHeader {
        pub fn parse(mut lines: Lines) -> Result<Self> {
            let request_line = lines.next().unwrap_or_default();
            let parts: Vec<_> = request_line.trim().split_whitespace().collect();
            if parts.len() != 3 {
                let err_msg = format!("Request header should consist of three parts. Got: {:?}",
                                      request_line);
                return Err(Error::new(ErrorKind::InvalidData, err_msg));
            }
            let (method, uri, protocol) = (parts[0], parts[1], parts[2]);

            match method {
                "GET" => Self::parse_get_header(uri, protocol, lines),
                _ => {
                    let err_msg = format!("Unsupported request method. Request line: {:?}",
                                          request_line);
                    Err(Error::new(ErrorKind::InvalidData, err_msg))
                }
            }
        }
    }

`Lines` jest iteratorem po kolejnych liniach napisu. Iteratorów (czyli typów
implementujących cechę `std::iter::Iterator`) można używać m.in. w pętlach
`for`, pobierać z nich kolejne elementy przy pomocy metody `next()` oraz
dokonywać na nich wiele innych operacji, które zobaczymy później.

    ::rust
    let request_line = lines.next().unwrap_or_default();

Tutaj właśnie odczytujemy pierwszą linię z obiektu `Lines`. `unwrap()` lub jego
inna forma sa tutaj konieczne. W tym wypadku, zadowolimy się jeśli w przypadku
braku pierwszej linii wynikiem będzie pusty napis.

    ::rust
    let parts: Vec<_> = request_line.trim().split_whitespace().collect();

Odcinamy białe znaki z obu końców `request_line` przy pomocy `trim()`.
`split_whitespace()` dzieli nasz napis w miejscach w których są białe znaki, zaś
`collect()` zbiera wynik i zwraca go w formie tablicy `Vec`.

W tym wypadku podpowiedzieliśmy kompilatorow, że `parts` będzie typu `Vec<_>`,
czyli zmienną będącą dynamiczna tablicą przechowywującą jakiś (`_`) typ. Jest to
o tyle ważne, że `collect()` może zwrócić dowolny obiekt spełniający cechę
`FromIterator`. Kiedy już jednak podpowiemy, że chodzi nam o `Vec`, to
kompilator już będzie w stanie sam uzupełnić sobie brakującą lukę `_`.

Jak widać, złożyliśmy tutaj po drodzę kilka funkcji, `trim()`,
`split_whitespace()` oraz `collect()`. Takie właśnie złożenia są powszechną
praktyką w językach funkcyjnych, ale także i w Ruscie. Skracają one kod, a
często pozwalają na dokonanie optymalizacji (kompilator od razu widzi, że nie
potrzebujemy pośrednich wyników, bo nie zapisujemy ich nigdzie).

Co ciekawe, zarówno `trim()` jak i `split_whitespace()` nie dokonują żadnego
kopiowania napisów, po prostu zwrając obiekty typu `&str` (czyli kawałki
zaalokowanego już gdzieś napisu).

    ::rust
    if parts.len() != 3 {
        let err_msg = format!("Request header should consist of three parts. Got: {:?}",
                              request_line);
        return Err(Error::new(ErrorKind::InvalidData, err_msg));
    }
    let (method, uri, protocol) = (parts[0], parts[1], parts[2]);

    let method = match method {
        "GET" => RequestMethod::Get,
        _ => {
            let err_msg = format!("Unsupported request method. Request line: {:?}",
                                  request_line);
            return Err(Error::new(ErrorKind::InvalidData, err_msg))
        }
    };

Poprawny nagłówek żądania HTTP powinien składać się z trzech części i tutaj
właśnie sprawdzamy czy tak faktycznie jest. Jeśli tak, przypisujemy je do
zmiennych o odpowiednich nazwach.

    ::rust
    // http/header.rs

    impl RequestHeader {
        // ...

        pub fn parse(mut lines: Lines) -> Result<Self> {
            // ...

            Ok(RequestHeader {
                   method: method,
                   uri: uri.to_owned(),
                   protocol: protocol.to_owned(),
                   fields: parse_fields(lines)?,
               })
        }
    }

Tak jak wcześniej wspomniałem, `trim()` oraz `split_whitespace()` nie kopiują
napisów, w związku z tym robimy to sami przy pomocy metody `to_owned()` typu
`&str`, która po prostu zwraca `String`. `parse_fields` jest funkcją, która
zajmie się odczytywaniem pół nagłówka.

### `parse_fields`
    ::rust
    // http/header.rs

    fn parse_fields(lines: Lines) -> Result<HashMap<String, String>> {
        let mut fields = HashMap::new();

        for line in lines.filter(|x| !x.is_empty()) {
            let parts: Vec<_> = line.trim().splitn(2, ": ").collect();
            if parts.len() != 2 {
                let err_msg = format!("Header field should have form \"X: Y\". Got: {:?}", line);
                return Err(Error::new(ErrorKind::InvalidData, err_msg));
            }
            fields.insert(parts[0].to_owned(), parts[1].to_owned());
        }
        Ok(fields)
    }

Tak jak poprzednio, argumentem wejściowym jest `Lines` (tym razem bez `mut`,
ponieważ nie będziemy zmieniać tego obiektu tak jak poprzednio przy pomocy
`next()`, bedziemy go sobie tylko "oglądać" przy pomocy innych metod).

Korzystamy z wbudowanej kolekcji `HashMap` aby przechowywać wartości pól.

    ::rust
    let mut fields = HashMap::new();

Dla każdej linii (która nie jest pusta), sparsujemy ją i podzielimy na nazwę
pola i wartość.

    ::rust
    for line in lines.filter(|x| !x.is_empty()) {
        let parts: Vec<_> = line.trim().splitn(2, ": ").collect();
        if parts.len() != 2 {
            let err_msg = format!("Header field should have form \"X: Y\". Got: {:?}", line);
            return Err(Error::new(ErrorKind::InvalidData, err_msg));
        }
        fields.insert(parts[0].to_owned(), parts[1].to_owned());
    }

`filter` jest metodą cechy `Iterator`, która przyjmuje predykat i zwraca
iterator, który ignoruje elementy nie spełniającego tego predykatu. W tym
przypadku, interesują nas tylko niepuste linie. Na każdej linii wykonujemy
znajomy nam `trim()`, a następnie dzielimy ją na co najwyżej dwie części (licząc
od lewej) przy napotkaniu ": ". Każde poprawnie sparsowane pole zapisujemy w
słowniku (`HashMap`) metodą `insert()` (pamiętając o zamianie `&str` na `String`
przy pomocy `to_owned()`).

Na końcu zwracamy nasz słownik jako `Ok(fields)`.

#### Funkcje anonimowe (closures)
Jak w większości współczesnych języków programowania, w Ruscie można korzystać z
funkcji anonimowych. Ich składnia jest następująca:

    ::rust
    |x, y, z| x + y + z

W przykładzie z poprzedniego akapitu skorzystaliśmy z nich do odsiania pustych
linii.

### `ResponseHeader`
Implementacja `ResponseHeader` wygląda bardzo podobnie, zarówno w kwestii
definicji struktury jak i parsowania, dlatego nie będę poświęcał jej zbyt wiele
czasu. Jedyną interesującą częścią, może być zamiana napisu zawierającego liczbę
na zmienną typu całkowitoliczbowego.

    ::rust
    let status_code = status_code
        .parse()
        .map_err(|_| {
                     Error::new(ErrorKind::InvalidData,
                                format!("Status code cannot be parsed. Got: {:?}", status_code))
                 })?;

Zmienna `status_code` jest póżniej zapisywana do pola o typie `u16`, więc
kompilator wie, której wersji metody `parse()` musi tutaj użyć. W przypadku
niepowodzenia, błąd zwracany przez `parse()` będzie jednak typu innego niż
`io::Result`, który zwracamy w metodzie `ResponseHeader::parse()`. W związku z
tym, trzeba przerobić jeden rodzaj błędu na drugi.

W poprzednim poście wspominałem jak można to robić, w tym wypadku jednak,
sytuacja jest jednorazowa, a dodatkowo chcemy dodać nieco więcej informacji o
tym, kiedy błąd nastąpił. W takich przypadkach przydaje się metoda `map_err()`,
która przyjmuje funkcję mającą za zadanie skonwertować jeden typ błędu na inny.

## Zapisywanie do obiektów z cechą `Writer`
Obiekty implementujące cechę `Writer` udostępniają m.in. metodę `write_all()`,
która przyjmuje wycinek tablicy (slice) bajtow (`u8`), aby ją zapisać. Pewnym
smutnym skutkiem ubocznym takiego interfejsu jest to, że cały obiekt trzeba
zakodować w formie `&[u8]` zanim przekaże się go pisarzowi. W przypadku
nagłówków HTTP, nie byłby to zapewne zbyt kosztowny proces, ale skoro możemy
zrobić to wydajniej, to czemu nie spróbować?

Jednym ze wzorców, które znam z C++ (`operator<<`) czy Go, jest implementowanie
przez obiekty przeznaczone do zapisu metody (nazwijmy ją `write_to`), która
przyjmuje `Writer` i zapisuje się do niego po kawałku, bez konieczności
budowania całego obiektu jako spójny ciąg bajtów. Zastanawiałem się, czy Rust
oferuje jakieś inne rozwiązania lub gotowe cechy, które tylko trzeba
zaimplementować. Zapytałem na kanale IRC **#rust-beginners** i okazało się, że
nie ma niczego podobnego w bibliotece standardowej i metoda taka jak:

    ::rust
    pub fn write_to<W: Write>(&self, w: &mut W) -> Result<()> {
        // ...
    }

wydaje się dobrym pomysłem.

W związku z tym, stworzymy sobie nowy plik `write_to.rs` w głównym katalogu
(`src`). A w `main.rs` dodamy linijkę `mod write_to;`.

`write_to.rs` zawierać będzie definicję cechy:

    ::rust
    // write_to.rs

    use std::io::Write;
    use std::io::Result;

    pub trait WriteTo<W: Write> {
        fn write_to(&self, w: &mut W) -> Result<()>;
    }

### `HttpStream::send()`

Mając zaimplementowaną cechę `WriteTo` dla `Response` i `Request`,
implementacja `send()` stanie się trywialna:

    ::rust
    // http/mod.rs

    pub struct HttpStream<'a> {
        // ...
        tcp_writer: BufWriter<&'a net::TcpStream>,
    }

    impl<'a> HttpStream<'a> {
        // ...
        pub fn send<WT>(&mut self, packet: &WT) -> Result<()>
            where WT: WriteTo<BufWriter<&'a net::TcpStream>>
        {
            packet.write_to(&mut self.tcp_writer)?;
            self.tcp_writer.flush()
        }
    }

`where` użyte jest tutaj dla wygody, aby nie zaciemniać deklaracji `send`.
Zamiast tego, możnaby po prostu napisać:

    ::rust
    pub fn send<WT: WriteTo<BufWriter<&'a net::TcpStream>>>(&mut self, packet: &WT) -> Result<()>
    {
        packet.write_to(&mut self.tcp_writer)?;
        self.tcp_writer.flush()
    }

ale wygląda to bardzo nieczytelnie.

Notacja `X: Y` oznacza w tym wypadku "typ X implementujący cechę Y". Na potrzeby
`send` oczekujemy, że `WT` będzie potrafiło zapisać się do `BufWriter`
opakowującego `TcpStream`.

### Implementacja cechy `WriteTo`

#### `Request`
    ::rust
    impl<W: Write> WriteTo<W> for Request {
        fn write_to(&self, w: &mut W) -> Result<()> {
            self.header.write_to(w.by_ref())?;
            w.write_all(self.body.as_slice())
        }
    }

W tej chwili wydaje mi się, że rozumiem konieczność użycia `by_ref()` (udało mi
się zaimplementować tę cechę bez użycia tej metody), ale nie chciałbym teraz o
tym opowiadać, dopóki nie będę w 100% pewien.  Prawdopodobnie będzie to materiał
na jeden z kolejnych postów.

#### `RequestHeader`
    ::rust
    impl<W: Write> WriteTo<W> for RequestHeader {
        fn write_to(&self, w: &mut W) -> Result<()> {
            write!(w,
                   "{method} {uri} {protocol}\r\n",
                   method = self.method,
                   uri = self.uri,
                   protocol = self.protocol)?;

            for (key, value) in self.fields.iter() {
                write!(w, "{}: {}\r\n", key, value)?
            }

            Ok(())
        }
    }

`write!` jest makrem podobnym do `println!`, które przyjmuje jako jeden ze
swoich argumentów format string, tyle tylko, że dodatkowo jako pierwszy argument
podajemy `Writer`. Po zapisaniu pierwszej linii (np. "GET /index.html
HTTP/1.1\r\n"), iteruję po polach nagłówka i zapisuje każde z nich w nowej
linii.

## Odesłanie pakietu
    ::rust
    // main.rs
    // ...

    fn handle_connection(tcp: net::TcpStream) {
        let mut h = http::HttpStream::new(&tcp);

        while !h.is_closed() {
            let request = match h.get_request().unwrap() {
                Some(r) => r,
                None => {
                    println!("UnexpectedEOF");
                    return;
                }
            };

            let mut response_body = Vec::new();
            request.write_to(&mut response_body).unwrap();

            let mut fields = HashMap::new();
            fields.insert("Content-Length".to_owned(), response_body.len().to_string());

            h.send(&http::Response {
                       header: http::ResponseHeader {
                           fields: fields,
                           protocol: request.header.protocol.clone(),
                           status_code: 200,
                           status_desc: "OK".to_owned(),
                       },
                       body: response_body,
                   });
        }
    }

Budujemy `http:Response` ustawiając status na `200 OK`, kopiujemy wersję
protokołu z żądania, oraz zapisujemy całe (łącznie z nagłówkiem) żadanie w
`response_body`, pamiętając o ustawieniu pola `Content-Length` w nagłówku.

## Podsumowanie
Uff! Ten post był wyjątkowo długi i napisanie go zajęło mi naprawdę dużo czasu.
Mam nadzieję, że poprzedni post (część 5) wyjaśnił trochę, co znaczą te
wszechobecne '?' i kod z tego wpisu jest nieco łatwiejszy do zrozumienia.

W kolejnym poście dodamy lepszą obsługę błędów (w tej chwili trudno jest
przetestować nasze proxy, ponieważ wysyłanie dowolnego innego zapytania niż
"GET" powoduje zakończenie pracy programu) i być może uprościmy korzystanie z
`http::Response` i `http::Request` (np. eliminując potrzebę ustawiania
`Content-Length` ręcznie).

# Pozostałe części
- następny post (część 7) w przygotowaniu
- [poprzedni post (część 5) (obsługa błędów, makra)](serwer-proxy-w-ruscie-czesc-5.html)

