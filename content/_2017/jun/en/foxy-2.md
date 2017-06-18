Title: Proxy server in Rust (part 2)
Date: 2017-06-18
Category: rust
Tags: rust, foxy
Summary: First draft and the basics of Rust.
lang: en


## Let's listen over TCP
This is how a draft of the main source file looks like (explanations below): 

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

### Listening
We're going to use the [`std::net`](https://doc.rust-lang.org/std/net/)
__crate__ (you can think of crates as libraries):

    ::rust
    use std::net;

[`std::net::TcpListener::bind`](https://doc.rust-lang.org/std/net/struct.TcpListener.html)
function is used here to start listening on port 4000 of the localhost.

    ::rust
    const PROXY_PORT: u16 = 4000;
    let listener = net::TcpListener::bind(("127.0.0.1", PROXY_PORT)).unwrap();


`u16` corresponds to `uint16` known from other languages, so `const PROXY_PORT:
u16 = 4000;` is a definition of a `PROXY_PORT` constant 16-bit integer equal to
4000.

What about the mysterious `unwrap()` at the end? Rust is a language designed
with safety with minimal runtime overhead in mind. How is this achieved in this
case? `bind()` could've simply returned `TcpListener`, but instead it returns
[`std::io::Result<TcpListener>`](https://doc.rust-lang.org/std/io/type.Result.html).

What's the difference?

Something may go wrong while trying to bind the socket (i.e. the port can be
already in use). This can be handled in many different ways (all with different
trade-offs):

- throwing an exception (Java, C++?),
- returning a pointer (C, C++),
- returning two values `(TcpListener, bool)` (Go),
- [`std::optional`](http://en.cppreference.com/w/cpp/utility/optional) (C++17).

Throwing an exception does not make the programmer handle it. Returning a
pointer or a `bool` value does not help here either. `std::optional` can be
simply ignored using `*`. Rust tries to follow a different path. Instead of the
abovementioned solutions, an object is returned in a wrapping (`Result`). This
type can be one of the two: the expected value of type `TcpListener` or an error
(`Error`)!

Since binding a socket to a port is vital for this program to run, the only
thing I do here is `unwrap()` the result.

What does this method do? If there is no error - the value is returned. If an
error happened, [`panic!`](https://doc.rust-lang.org/std/macro.panic.html) is
called (similar to [`panic`](https://blog.golang.org/defer-panic-and-recover)
known from Go).

### Accepting a connection
    ::rust
    match listener.accept() {
        Ok((sock, _)) => handle_connection(sock),
        Err(e) => panic!("Error while accepting connection: {}", e),
    }

If everything went smoothly, call `handle_connection(sock)` which will care take
of the rest.

If not, `panic!` with an appropriate error message.

### Pattern matching (`match`)
`match` is a language construct used mostly in functional languages (like
OCaml, Haskell, Lisp) rather than imperative ones (C, Python, Java, C++) and
that's why I'd like to say a few words about it.

[**Pattern matching**](https://en.wikipedia.org/wiki/Pattern_matching) is used
for:

- checking whether the object is what we think it is (in the above code, whether
  it's `Ok` (a value) or `Err` (an error))
- dissecting it (`Ok` is here made of two parts, the first one is the TCP
  socket, the second is the address; I'm ignoring the adress (using `_`), but
  binding the `sock` variable to the socket).


For example, if we were to write a simple calculator based on trees of
arithmetic expressions, a part of code might have looked like this:

    ::rust
    match expression {
        Add(x, y) => x + y,
        Sub(x, y) => x - y,
        Mul(x, y) => x * y,
        Div(x, y) => x / y,
    }

This language construct is possible thanks to types that are an disjunction of
different possible values. In this case it means that the expression can be i.e.
an addition or substraction. The information about the kind of expression is
stored and retrieved at runtime. What's important is the fact that the compiler
can check whether we've covered all the possible kinds (and warn us if we forget
about one).

We could've simulated it in C++ in a following way:

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

As you can see, pattern matching is pretty convenient. In the languages that
support it natively, the implementation is better than what I have shown here in
C++. Unfortunately, I don't know enough about Rust to talk about its internals
in this case.

### `panic!` and `{}`
`panic!` is a macro (right now we can think of it as a function, but `!` in Rust
is an indicator of a macro call) used for critical program errors.

`panic!` receives an argument list similar to `printf` known from other
programming languages, and `{}` is used to print the values of any type (not
exactly, more on that later).


## What's coming up?
In the next posts I plan to talk about:

- handling HTTP requests in different threads
- ownership and borrowing (the main characteristic of Rust that differentiates
  it from popular modern programming languages)
- creating structures
- methods
- traits
- expressions and statements
- and many, many more.

# Other parts
- [next post (part 3)](proxy-server-in-rust-part-3.html)
- [previous post (part 1)](proxy-server-in-rust-part-1.html)
