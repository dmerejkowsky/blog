---
authors: [dmerej]
slug: killing-unwrap
date: 2019-01-30T19:11:26.380880+00:00
draft: false
title: "Killing unwrap()"
tags: [rust]
summary: A collection of snippets to avoid unnecessary calls to unwrap() in Rust
---

# Wait, what? Who do you want to kill?

In Rust, to indicate errors or absence of a value we use types named `Result` and `Option` respectively.

If we need the *value* of an Result or Option, we can write code like this:

```rust
let maybe_bar = get_bar();
// bar is now an Option<String>
if maybe_bar.is_some() {
  let bar = bar.unwrap();
  // now bar is a String
} else {
  // handle the absence of bar
}
```

This works well but there's a problem: if after some refactoring the `if` statement is not called, the entire program will crash with: `called Option::unwrap on a None value`.

This is fine if `unwrap()` is called in a test, but in production code it's best to prevent panics altogether.

So that's the why. Let's see the how.

# Example 1 - Handling None

Let's go back to our first example: we'll assume there is a `bar::return_opt()` function coming from an external crate and returning an `Option<Bar>`, and that we are calling it in `my_func`, a function also returning an option:

```rust
fn my_func() -> Option<Foo> {
  let opt = bar::return_opt();
  if opt.is_none() {
    return None;
  }
  let value = opt.unwrap();
  ...
  // doing something with `value` here
}
```

So how do we get rid of the `unwrap()` here? Simple, with the *question mark operator*:

```rust
fn my_func() -> Option<Foo> {
  let value = bar::return_opt()?;
  // Done: the question mark will cause the function to
  // return None automatically if bar::return_opt() is None
  ...

  // We can use `value` here directly!
}
```

If `my_func()` does not return an `Option` or a `Result` you cannot
use this technique, but a `match` may be used to keep the "early return"
pattern:

```rust
fn my_func() {
  let value = match bar::return_opt() {
      None => return,
      Some(v) => v
  };
  ...
}
```

Note the how the `match` expression and the `let` statement are combined. Yay Rust!


# Example 2 - Handling Result

Let's see the bad code first:

```rust
fn my_func() -> Result<Foo, MyError> {
  let res = bar::return_res();
  if res.is_err() {
    return Err(MyError::new(res.unwrap_err());
  }
  let value = res.unwrap();
  ...
}
```

Here the `bar::return_res()` function returns a `Result<BarError, Bar>` (where
`BarError` and `Bar` are defined in an external crate). The `MyError` type is in the current crate.

I don't know about you, but I really hate the 4th line: `return Err(MyError::new(res.unwrap_err());` What a mouthful!

Let's see some ways to rewrite it.

## Using From

One solution is to use the question mark operator anyway:

```rust
fn my_func() -> Result<Foo, Error> {
  let value = bar::return_res()?;
}
```

The code won't compile of course, but the compiler will [tell you what to do]({{< ref "post/0092-letting-the-compiler-tell-you-what-to-do.md" >}}),
and you'll just need to implement the `From` trait:

```rust
impl From<BarError> for MyError {
    fn from(error: BarError) -> MyError {
        Error::new(&format!("bar error: {}", error))
    }
}
```

This works fine unless you need to add some context (for instance, you may have an `IOError` but not the name of the file that caused it).

## Using map_err

Here's `map_err` in action:

```rust
fn my_func() -> Result<Foo, Error> {
  let res = bar::return_res():
  let some_context = ....;
  let value = res.map_err(|e| MyError::new(e, some_context))?;
}
```

We can still use the question mark operator, the ugly `Err(MyError::new(...))`
is gone, and we can provide some additional context in our custom Error type. Epic win!

# Example 3 - Converting to Option

This time we are calling a function that returns an `Error` and we want a `Option`.

Again, let's start with the "bad" version:

```rust
fn my_func() -> Result<Foo, MyError> {
  let res = bar::return_opt();
  if res.is_none() {
    retrun Err(MyError::new(....));
  }
  let res = res.unwrap();

  ...
}
```

The solution is to use `ok_or_else`, a bit like how we used the `unwrap_err` before:

```rust
fn my_func() -> Result<Foo, MyError> {
  let value = bar::return_opt().ok_or((MyError::new(...))?;
  ...
}
```

# Example 4 - Assertions

Sometime you may want to catch errors that are a consequence of faulty logic within the code.

For instance:

```rust
let mystring = format!("{}: {}", spam, eggs);
// ... some code here
let index = mystring.find(':').unwrap();
```

We've built an immutable string with `format()` and we put a colon in the format string. There's no way for the string to *not* contain a colon in the last line, and so we *know* that `find` will return something.

I reckon we should still kill the `unwrap()` here and make the error message clearer with `expect()`:

```rust
let index = mystring.find(':').expect("my_string should contain a colon");
```
# In tests and main

*Note: I'd like to thank Jeikabu whose [comment on dev.to](https://dev.to/jeikabu/comment/8kb4) triggered the addition of this section*:

Let's take another example. Here is the code under test:

```rust
struct Foo { ... };

fn setup_foo() -> Result<Foo, Error> {
    ...
}

fn frob_foo(foo: Foo) -> Result<(), Error> {
    ...
}
```

Traditionally, you had to write tests for `setup_foo()` and `frob_foo()` this way:

```rust
#[test]
fn test_foo {
  let foo = setup_foo().unwrap();
  frob_foo(foo).unwrap();
}
```

But since recent versions of Rust you can write the same test this way:

```rust
#[test]
fn test_foo -> Result<(), MyError> {
  let foo = setup_foo()?;
  frob_foo(foo)
}
```

Another big win in legibility, don't you agree?

By the way, the same technique can be used with the `main()` function (the entry point for Rust executables):

Old version:
```rust
fn main() {
    let result = setup_foo().unwrap();
    ...
}
```

New version:
```rust
fn main() -> Result<(), MyError> {
    let foo = setup_foo()?;
    ...
}
```


# Closing thoughts

When using `Option` or `Result` types in your own code, take some time to read
(and re-read) the documentation. Rust standard library gives you many ways to
solve the task at hand, and sometimes you'll find a function that does exactly
what you need, leading to shorter, cleaner and more idiomatic Rust code.

If you come up with better solutions or other examples, please let me know!
Until then, happy Rusting :)



[^1]: Yes, I'm using TDD, but this post is not about testing. Feel free to read [my other articles](/tags/testing) on the subject, though :).
