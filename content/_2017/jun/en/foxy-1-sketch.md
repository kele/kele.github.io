Title: Proxy server in Rust (part 1)
Date: 2017-06-17
Category: rust
Tags: rust, foxy
Summary: Learning Rust by writing a simple proxy server.
lang: en


# What this is all about

## Motivation
I'm constantly distracting myself. Very often I visit sites like Hacker News or
lobste.rs even though I don't have time to read the articles. As one can
imagine, it doesn't help very much with being productive. I don't really have
this problem when I'm busy and focused, but when I have 2-3 minutes to spare
(because the project is building, my map-reduce is running or I'm waiting for a
reply), my habit is to skim through every website that I find at least mildly
interesting.

I've tried different Chrome extensions, changes in `/etc/hosts` or blocking some
domains on my home router, but none of these were flexible enough for me so I
ended up working around them. This is where the idea of writing my own proxy
server came from. The list of features should include:

- redirecting,
- time based blocking,
- delaying (if a site loads slowly, I tend to realize that I shouldn't be doing
  this),
- etc.

## Why Rust?
The language I used the most was always C++. At work I'm using mostly Go now.
Although, the idea of having a strong compiler definitely speaks to me. That's
why I wanted to learn Rust. Also, a proxy server seems to be a project easy
enough that it won't distract me too much from learning the language itself, but
hard enough to see whether I like Rust or not.

## What can you expect?
This is going to be a journal of my adventure with Rust. I have never ever used
this language, so it's not going to be a tutorial of **how to write good Rust**,
but I'm definitely going to try my best to learn as much as possible and share
the knowledge. I have an idea what the borrow checking is about and I have some
experience with rich type systems (Hindley-Milner from OCaml), so I hope I won't
be lost completely. :)


# Preparations

## Compiler
Instalation is very simple: [rustup.rs](https://rustup.rs/). Some of the Linux
distros are going to have Rust in their repositories already.

For convenience, most of the operations (creating projects, building, running)
are done by using a tool called `cargo`'. Please, do not forget to install it if
you're not using rustup.rs.

## Documentation and other learning resources
There are lots of good materials for learning Rust. The primary official
document of the language and the standard library documentation can be both
found at [rust-lang.org](https://www.rust-lang.org/).

## My programming environment
VIM + [Racer](https://github.com/phildawes/racer) +
[vim-racer](https://github.com/racer-rust/vim-racer). Racer is an
auto-completion tool for Rust.

## Creating a new project
    ::bash
    cargo new --bin project

This command creates a template of an executable  (`--bin`) named `project`.
What's interestinghere is that the project is going to be created under Git
versioning control system by default (nice gesture ;)).

`cargo build` builds the project. The default template is the well known **Hello
World**.

# The end of the first post
It's all for today. In the next post there will be some code, I promise! :)

# Other parts
- [next post (part 2)](proxy-server-in-rust-part-2.html)
