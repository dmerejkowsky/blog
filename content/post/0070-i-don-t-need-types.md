---
authors: [dmerej]
slug: trying-mypy
date: 2018-05-27T10:17:17.789657+00:00
draft: false
title: I don't need types
tags: [misc]
---

This is a story about me being wrong about tests and type systems.

It's also a story of me trying something new and learning a few things.

Let's start at the beginning.

# C++ vs Python

A few years ago, I was working in a team where the two main languages used were C++ and Python.

Here's what I used to think:

C++ sucks:

* I have to specify types everywhere:
  * I need to know the difference between `int`, `long`, `uin8_t`, `size_t` even if all I want is a goddamn integer.
  * I have to duplicate the signatures of the methods and functions in the header and the source files
* I never know if a compiler warning or error indicates a bug or not
* There's still a lot of bugs the compiler does not catch (race conditions, dangling pointers ....)
* Refactoring is hard: when you change a function signature, you have to fix the code everywhere before you can even run some tests.
* Writing tests in hard: You can't really write isolation tests because mocking and dependency injection in C++ don't really work. Plus, `gtest` sucks.

Python rocks:

* I don't have to think about types if I don't want to. If I *really* need it, I can write an abstract base class, but most of the time duck-typing "just works".
* If I misspell a variable or function name, or if I forgot to import a module, I'll get a test failure immediately.
* For each bug I can quickly add a non-regression test.
* Refactoring is easy: all you have to do is run the tests, look at the failures and fix the code. When the tests pass, you know you're done.
* Writing tests is easy: dependency injection is trivial thanks to duck-typing, and you can monkey-patch or mock everything! Plus, `pytest` is awesome!
* Static analysis for Python does not work, pylint is slow, and hard to configure. There are tons of bugs it does not catch, and it is often wrong.
* Types annotations are useless (after all, the interpreter does almost nothing with them), except maybe for documentation purposes.

{{< note >}}
I now think **most of these statements are wrong**, but it was what I believed at the time.
{{</ note >}}

# Changing my mind

So there I was. Tools and type systems did not matter, all that matter were tests and how easy it was to write them. I did not need a type system because tests were enough.

<center>⁂</center>

Boy, was I wrong... Here's a list of things that contributed to burst my bubble.


## Some linters

### pyflakes

I started using [pyflakes](https://github.com/PyCQA/pyflakes) with [vim-ale](https://github.com/w0rp/ale)[^1].

pyflakes is very easy to use, requires no configuration and is fast.

Suddenly a whole bunch of bugs disappeared: pyflakes is very good at finding misspelled variables or missing imports.

So maybe writing tests just to find misspelled variables or missing imports is overkill?

Of course, pyflakes does not catch other errors like calling a function with an incorrect number of arguments but still, it's quite nice to catch these errors *right after the file is saved*, instead of later when a test fails.


### pylint

I've already mentioned how [pylint can be very useful]({{< ref "post/0018-some-pylint-tips.md" >}}) if you take the time to configure it properly, so I won't repeat myself here.

Still, I learned that Python static analyzers did not have to suck after all, and could find defects faster than tests.

Today I use pyflakes, pylint and a few other linters for all my Python projects. You can read more about this in
[How I lint my Python]({{< ref "post/0037-how-i-lint-my-python.md" >}}).

At this point I had changed my mind a little bit. They were tools other than tests that could be useful. But I was still thinking that types did not help nearly as much as tests did.

## A talk

And then I watched a talk called [ideology](https://www.destroyallsoftware.com/talks/ideology), by Gary Bernhardt. I highly recommend it.

Excerpt:

> [This is important] mostly because it will make you better programmers, but also because it will stop you from making angry Hacker News comments.


I won't summarize the talk here, but it helped me realizing what I really meant when I claimed "I have tests so I don't need types".

But this was rather abstract. Changing my mind about tests required me working
with programming languages other than C++ and Python.


## Javascript

Last year I had to make a refactoring in a Javascript project.

There were *no tests at all*, and adding them would have been pretty challenging.

But there were [flow](https://flow.org/) type annotations everywhere. The errors weren't
always easy to understand and even sometimes misleading, but flow did help me gain
confidence that I was not breaking everything during the refactoring.

That showed me that type annotations in a "dynamic" languages could actually be worth it.

Still, I was convinced we should have written tests for this project since day one, and not let
the production code grow without tests.

Type annotations were required *because* they were no tests, and surely tests alone would have suffice.

## Rust

Rust was the last nail in the coffin.

I started re-writing a Python project in Rust, and suddenly all this stuff
about "if it compiles, it works", and "types system make unit tests
unnecessary" finally started to make sense.

Here's what I learned using Rust:

* Specifying types is easy: all you need to annotate are function parameters and
  return values, and everything else is inferred by the compiler.
* Error messages and warnings almost always indicate a bug or an inefficient way of doing things.
* And types can actually help you!

Let me give you a few examples:

* Anything that can fail returns a *type* (like `Option` or `Result`) that
  forces you to handle errors.
* There is a `Copy` *trait* that tells you whether a type has copy semantics versus move semantics.
* The `Send` and `Sync` traits define how you can use a type across threads.
* and more!

In the mean time, using TDD with Rust is enjoyable and even recommended in [the Rust book](https://doc.rust-lang.org/stable/book/second-edition/index.html).
I even wrote a test to make sure a certain bug would be caught *at compile time*.

And that's how I completely changed my mind: type system do not have to suck,
they can be very useful, and you can *combine* them with tests to get the
best of two worlds.

# Conclusion and teaser

You see, we are terrible at spotting errors in our own code.

That's why we try and multiply the techniques hoping each of them will find different types of mistakes:

* We ask other humans to look at our code, during code reviews or peer programming
* We ask other humans to find defects in the code for us, and we call this "a QA process"
* We use static analyzers to find issues in the code automatically
* We use tests to try and prove that the code works as it should
* We use TDD to look at the code both from the 'production' perspective (when we go from red to green), and from a 'quality' perspective (when we go from green to refactor).
* And we use static types or type annotations to improve correctness of the
  code in a way that complements all of the above methods.

That's all for today.

If you still believe that Python does not need types if you have a good tests, I'll have some very concrete examples to show you in a future blog post.

Cheers!

[^1]: If using this kind of linters sounds interesting to you, you can read my [blog post]({{< ref "post/0047-lets-have-a-pint-of-vim-ale.md" >}}) on the subject.
