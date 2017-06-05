
Chcielibyśmy móc, chociażby do debugowania, być w stanie taki odebrany pakiet
wyświetlić. Dodajmy sobie nową linijkę do `handle_connection`:

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

            println!("Got: {:?}", request.to_string()); // o, tutaj!
            // ...
        }
    }

A następnie, implementację metody `to_string()` dla `HttpPacket`.

    ::rust
    // http/mod.rs

    // ...

    use std::string;

    impl HttpPacket {
        pub fn to_string(&self) -> string::String {
            "TODO: HttpPacket.to_string() is not yet implemented".to_string()
        }
    }

Czemu zdecydowałem się zwrócic `string::String` poprzez wywołanie `to_string()`
wyjaśnię przy okazji omawiania cech (trait).
