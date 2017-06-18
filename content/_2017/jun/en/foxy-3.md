Title: Proxy server in Rust (part 3)
Date: 2017-06-19
Category: rust
Tags: rust, foxy
Summary: Ownership and borrowing, structures, methods - writing an echo server.
lang: en

Code available [here](https://github.com/kele/foxy/tree/part3).

## HTTP protocol library
There exists a pretty mature library for handling HTTP protocol for Rust already
- [**hyper**](https://github.com/hyperium/hyper). Amongst the others it's used
by [**Servo**](https://github.com/servo/servo) - probably the most prominent
Rust project to date.

Nevertheless, I wouldn't learn much by just settling to use an external library,
so I'm going to write my own HTTP protocol handling module.

## Creating a new module
Rust code is organized in **crates** which consist of **modules**. Crates
correspond to libraries known from other languages and modules to packages. Each
crate has it's **root module** which can have submodules as it's descendants.

To use a module we need to declare it first:

    ::rust
    mod http;

<a name="backref-1"></a>
Rust<sup>[1](#rust-i-cargo)</sup> will then expect a `http.rs` or `http/mod.rs`
source file. In one of these places we're going to write our code for HTTP
handling.

    ::rust
    // http/mod.rs
    pub struct HttpStream {

    }

The `struct` keyword is used to define new structures and `pub` is used for
making it externally visible (like `public` in C++ or Java).

## Designing the API and the ownership model
We already know where we want to put our code so it seems like a good time to
start designing the API.

The main object will be `http::HttpStream` - a wrapper for `net::TcpStream` with
a few HTTP specific functionalities added. It is also going to **own** the
`TcpStream`. That being said, we need to talk a bit about the Rust ownership
model.

## Ownership and borrowing
The ownership model is probably the most distinct feature of Rust amongst the
popular modern programming languages.

In Rust, an object can be passed to a function in three different ways:

    ::rust
    let mut x = T{};

    foo(x);
    bar(&x);
    xyz(&mut x);

### `foo(x)`
In this case `x` is passed to `foo()` **by value**. In Rust it means one of two
things:

- `x` is going to be copied (if it implements the `Copy` trait, more on that
  later)
- **the ownership of `x` is passed to `foo()`** (or, `x` is moved).

In the second case `x` cannot be used after the call to `foo()`!. For example: 

    ::rust
	struct X { }
	fn foo(x :X) { }

	fn main() {
		let x = X{};
		foo(x);
		foo(x); // WRONG
	}

trying to compile the above code will result in an error:

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

After `x` is moved to `foo()` we no longer have access to it. This semantics
allows the compiler to do following things:

- forbid using `x` after it was moved,
- accurately decide which piece of code is responsible for freeing the memory
  belonging to `x` (in this case, `foo` is).

This is how Rust can achieve memory safety with no runtime overhead (no
reference counting, no garbage collecting).

### `bar(&x)`
`&x` in Rust indicates a **borrow**. After `bar()` finishes it's work it has to
give `x` back in an untouched state. This means that `x` is lended to `bar()` in
a **read only** way.

This allows us to safely write code such as:

	::rust
	bar(&x);
	bar(&x);

because after every `bar(&x)` call we're getting `x` back. The compiler then
knows that:

- `bar` doesn't have to free the memory of `x`,
- `bar` cannot keep `x` forever (what does this actually mean is a more
  complicated topic and we're going to cover it when discussing **lifetimes**).

### `xyz(&mut x)`
Similarly to `&x`, but this time we're lending the object with permission to
change it. Without discussing **lifetimes** we cannot really talk more about the
differences between `&` and `&mut`, please be patient. :)

## Designing the API (continued)
Knowing how Rust handles argument passing we can start thinking about using the
new `HttpStream` object. At first, we're going to write an **echo server**,
which means that we're going to send back whatever we've received.

	::rust
	// main.rs

	// ...

	mod http;

	fn handle_connection(tcp: net::TcpStream) {
		let mut h = http::HttpStream::new(tcp);

        // ... main loop here ...
	}

We are going to move the TCP socket to a new `HttpStream` object. The
definition of `HttpStream` looks as follows:

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

`impl` is used for implementing methods for a given structure. As one can see,
`pub` is used on method granularity in Rust. In this case, `new` is an
**associated function** (in other languages that would be called a static
method), which means that it does not need to receive the object of the type
it's associated with but it still has access to the private fields and methods
of this type. This is why it's called as `HttpStream::new()` and not `h.new()`.

The only duty of `new` is to pass `tcp` to `HttpStream`, because we don't really
want `tcp` to be a public field.

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

There are two new methods here: `is_closed()` and `get()`.

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

<a name="backref-2"></a>
`get` will be used for receiving HTTP packets, so it needs to:

- have <span style="text-decoration:
  line-through">mutable</span><sup>[2](#mutable-tcp)</sup>  access to the `tcp`
  field through `self` (like in Python, or `this` in C++)
- return `io::Result<HttpPacket>` because as [I mentioned
  earlier](proxy-server-in-rust-part-2.html), something may go wrong while
  receiving the packet and we would like to handle the error.

Right now the it's a dummy implementation so it just returns an empty packet
(wrapper with `Ok`).

`is_closed()` is a predicate that tells us whether the connection is closed or
not.

We need a new `HttpPacket` structure representing an HTTP packet.

    ::rust
    // http/mod.rs

    // ...

    pub struct HttpPacket {}


One more thing to do in the main loop is to send back the packet.

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

And here's a dummy implementationof `send`:

    ::rust
    // http/mod.rs

    // ...

    impl HttpStream {
        // ...

        pub fn send(&mut self, packet: &HttpPacket) io::Result<()> {
            Ok(())
        }
    }

Here, `send` might return an error but if everything goes smoothly there's
nothing to return. In this case, the `()` (unit) type is used (which
corresponds to `void` known from other languages).

## Summary
We didn't manage to write any working code (at least it compiles!) but we've
talked about some key features of Rust. Without discussing them it wouldn't be
possible to understand any meaningful code.

In the next post I hope to implement a simple echo server.

# Other parts
- [next post (part 4)](proxy-server-in-rust-part-4.html)
- [previous post (part 2)](proxy-server-in-rust-2.html)

<hr>

### Footnotes

<a name="rust-i-cargo"></a><sup>1</sup> In the official docs "Rust" is used as
both the language itself and `cargo`.  ([go back](#backref-1))
<a name="mutable-tcp"></a><sup>2</sup> This is a late translation of a post in
Polish, so I already know that the `read()` method is also implemented for `&'a
net::TcpStream` - no mutability needed here. ([go back](#backref-2))
