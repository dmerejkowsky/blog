---
authors: [dmerej]
slug: killing-unwrap
date: 2019-01-30T19:11:26.380880+00:00
draft: true
title: "Killing unwrap()"
tags: [rust]
summary: A collection of snippets to avoid unnecessary calls to unwrap() in Rust
---

[Rust](/tags/rust) quickly become my second favorite language. I think it
I think I fell in love 9 months ago while reading the [Rust book](https://doc.rust-lang.org/book/) for the second time.

Anyway, writing Rust code is still challenging for me (but it's also part of the fun!).

Here's what my process looks like at this point:

1. Start by writing a failing test [^1]
2. Make the code compile, At this point I'm focusing on making the failing test pass. Thus, I'll often use `unwrap()` so that I don't have to think about error handling at this stage.
3. Make the borrow checker pass. Go back to 2/ if pleasing the borrow checker breaks the compilation ...
4. Make the test pass
5. Refactor. Go back to 2/ if the refactoring breaks compilation or borrow checking). I often experience problems when introducing new structs, traits or extracting functions, but I'm slowly getting better at it.


What I've discovered is that calling `unwrap()` is almost always a code smell - there's often a better way to deal with functions that return Option or Error. Below is a list of useful patterns I've collected.

I'm sharing this in the hope it will help you too. Also, many thanks to all the nice people who agreed to review my Rust code!



# Example 1

Let's start with a simple example: we'll assume there is a `bar::return_opt()` function coming from an external crate and returning an `Option<Bar>`.

We want to return immediately if the value is none.

Here's a non-optimal way to do it:

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

Why is it bad? Because you can use the question mark operator instead:

```rust
fn my_func() -> Option<Foo> {
  let value = bar::return_opt()?;
  // Done: the question mark will cause the function to
  // return None automatically if bar::return_opt() is None
  ...

  // We can use value` here directly!
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

Note how we use the `match` statement together with the `let` expression. Yay Rust!


# Example 2

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

# Example 3

This time we are calling a function that returns an `Error` and we want a `Option`.

Again, let's start with the "bad" version:

```rust
fn my_func() -> Result<Foo, MyError> {
  let res = bar::return_opt();
  if res.is_none() {
    retrun Err(MyError::new(....);
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

# Closing thoughts

When using `Option` or `Result` types in your own code, take some time to read
(and re-read) the documentation. Rust standard library gives you many ways to
solve the task at hand, and sometimes you'll find a function that does exactly
what you need, leading to shorter, cleaner and more idiomatic Rust code.

If you come up with better solutions or other examples, please let me know!
Until then, happy Rusting :)

[^1]: Yes, I'm using TDD, but this post is not about testing. Feel free to read [my other articles](/tags/testing) on the subject, though :).
