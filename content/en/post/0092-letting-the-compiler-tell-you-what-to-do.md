---
authors: [dmerej]
slug: letting-the-compiler-tell-you-what-to-do
date: "2019-01-12T12:26:27.325275+00:00"
draft: false
title: "Letting the compiler tell you what to do - an example using Rust"
tags: [rust]
summary: "What happens when you let the compiler tell you what to do? Let's find out with a simple example in Rust."
---

If you've ever written code in a compiled language (C, C++, Java, ...), you are probably used to compiler error messages, and you may think there are only here to prevent you from making mistakes.

Well, sometimes you can also use compiler error messages to *design and implement new features*. Let me show you with a simple command-line program written in Rust.

# An example

Here's the code we have written so far:

```rust
use structopt::StructOpt;

#[derive(Debug, StructOpt)]
struct Opt {
    #[structopt(long = "--dry-run")]
    dry_run: bool,
}

fn main() {
    let opt = Opt::from_args();

    let dry_run = opt.dry_run;
    println!("dry run: {}", dry_run);
}
```

We implemented a `--dry-run` option using the [structopt crate](https://github.com/TeXitoi/structopt).

Now we want to add a `--color` option that can have the following values: `never`, `always`, and `auto`.

But structopt (nor clap, which it is based on) does *not* have the concept of "choice", like `argparse` or `docopt`.

So we *pretend* it does and we write:

```rust
enum ColorWhen {
    Always,
    Never,
    Auto,
}

#[derive(Debug, StructOpt)]
struct Opt {
    #[structopt(long = "--dry-run")]
    dry_run: bool,

    #[structopt(
        long = "--color",
        help = "Whether to enable colorful output."
    )]
    color_when: ColorWhen,
}

fn main() {
  let opt = Opt::from_args();
  let dry_run = opt.dry_run;
  let color_when = opt.color_when;

  println!("dry run: {}", dry_run);
  println!("color: {}", color_when);
}
```

*Note: this is sometimes called "programming by wishful thinking" and can be used in various situations*.

Anyway, we try and compile this code and are faced with a bunch of compiler errors.

And that's where the magic starts. We are going to make this work *without* opening structopt's documentation and by *only* following the advice given by the compiler, one error after the other. Ready? Let's go!


## Error 1


```
color_when: ColorWhen,
   |     ^^^^^^^^^^^^^^^^^^^^^ `ColorWhen` cannot be formatted using `{:?}`
   |
   = help: the trait `std::fmt::Debug` is not implemented for `ColorWhen`
   = note: add `#[derive(Debug)]` or manually implement `std::fmt::Debug`
```

We do what we are told, and add the `#[derive(Debug)]` annotation:

```rust
#[derive(Debug)]
enum ColorWhen {
  // ...
}
```

Well, that what easy. Let's move on to the next error.

## Error 2


```
  | #[derive(StructOpt)]
  |          ^^^^^^^^^ the trait `std::str::FromStr` is not implemented for
  |                    `ColorWhen`
```

The compiler tells us it does not know how to convert the command line argument (a string) into the enum.

We don't really remember what the `FromStr` trait contains. We could look up the documentation (but that would be cheating), so instead we write an empty implementation and see what happens:

```rust
impl std::str::FromStr for ColorWhen {

}
```

## Error 3

Again, the compiler tells us what to do:

```
not all trait items implemented, missing: `Err`, `from_str`
  --> src/main.rs:10:1
   |
10 | impl std::str::FromStr for ColorWhen {}

missing `Err`, `from_str` in implementation
note: `Err` from trait: `type Err;`
note: `from_str` from trait:
  `fn(&str) -> std::result::Result<Self, <Self as std::str::FromStr>::Err>`
```

We need an [associated type](https://doc.rust-lang.org/book/ch19-03-advanced-traits.html#specifying-placeholder-types-in-trait-definitions-with-associated-types) `Err`, and a `from_str()` function.

Let's start with the Err type. We'll need to tell the user about the invalid `--color` option, so let's use an enum with a `InvalidArgs` struct containing a description:

```rust
#[derive(Debug)]
enum FooError {
  InvalidArgs { details: String },
}
```

Note how the compiler almost "forced" us to have our own error type, which is a very good practice!

Anyway, along with the `from_str` function.


```rust

impl std::str::FromStr for ColorWhen {
    type Err = FooError;

    fn from_str(s: &str) -> Result<ColorWhen, FooError> {
        match s {
            "always" => Ok(ColorWhen::Always),
            "auto" => Ok(ColorWhen::Auto),
            "never" => Ok(ColorWhen::Never),
            _ => {
                let details = "Choose between 'never', 'always', 'auto'";
                Err(FooError::InvalidArgs { details: details.to_string() })
            }
        }
    }
}
```


## Error 4

```
error[E0599]: no method named `to_string` found
  for type `FooError` in the current scope
```

All custom error types should be convertible to strings, so let's implement  that:

```rust
impl std::string::ToString for FooError {
    fn to_string(&self) -> String {
        match self {
            FooError::InvalidArgs { details } => details.to_string(),
        }
    }
}
```

It compiles!

Let's check error handling:

```test
$ cargo run -- --color foobar
error: Invalid value for '--color <color_when>':
  Choose between 'never', 'always', 'auto'
```

Let's check with a valid choice:

```bash
$ cargo run -- --color never
dry run: false
color: Never
```

It works!


## The default

There's still a small problem: we did not use a `Option` for the `color_when` field, so the `--color`
command line flag is actually required:

```bash
$ cargo run
error: The following required arguments were not provided:
    --color <color_when>
```

Can't blame Rust there. That's our fault for not having used an optional ColorWhen field in the first place.

Let's try and fix that by using an `Option<>` instead:

```rust
// ...
struct Opt {
    // ...
    #[structopt(
        long = "--color",
        help = "Whether to enable colorful output"
    )]
    color_when: Option<ColorWhen>,
}
```

Well, since we did not do anything with the `opt.color_when` but print it, everything still works :)

## Error 5

Had we tried to use the option directly like this:

```rust
fn force_no_color() {
  // ...
}

fn main() {
  let color_when = opt.color_when;

  match color_when {
    ColorWhen::Never => force_no_color(),
    // ..
  }
```

The compiler would have told us about our mistake:

```
ColorWhen::Never => force_no_color(),
^^^^^^^^^^^^^^^^ expected enum `std::option::Option`, found enum `ColorWhen`
```

And we would have been forced to handle the default value, for instance:

```rust
let color_when = color_when.unwrap_or(ColorWhen::Auto);
```

## Side note

There's an other cool trick we can use to achieve the same result, by leveraging the `default` trait:


```rust
#[derive(Debug)]
enum ColorWhen {
    Always,
    Never,
    Auto,
}

impl std::default::Default for ColorWhen {
    fn default() -> Self {
        ColorWhen::Auto
    }
}
```

And calling `unwrap_or_default()` instead of `unwrap_or()`:

```rust
fn main {
    let color_when = opt.color_when.unwrap_or_default();
}
```

The code is a bit longer but I find it more readable and more "intention revealing".

(End of side note)

## Conclusion


I hope this gave you new insights about what a good compiler can do, or at least a feel of what writing Rust looks like.

I call this new workflow "compiler-driven development" and I find it nicely complements other well-known workflows like TDD.

*Final note: to be honest we could have achieved better results by reading the documentation too: for instance, we could have used a [custom string parser](https://docs.rs/structopt/0.2.14/structopt/#custom-string-parsers) instead of the `FromStr` boilerplate, and implemented the Display trait on our [custom error](https://doc.rust-lang.org/rust-by-example/error/multiple_error_types/define_error_type.html) instead. Good docs matter too ...*

Cheers!
