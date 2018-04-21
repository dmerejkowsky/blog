---
slug: trying-mypy
date: 2018-04-21T10:17:17.789657+00:00
draft: false
title: "Trying mypy"
tags: [python]
---

This is a story about me being wrong about tests and type systems.

It's also a story of me trying something new and learning a few things.

Let's start at the beginning.

# I don't need types

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
* Writing tests is easy: dependency injection is trivial to do thanks to duck-typing, and you can monkey-patch or mock everything! Plus, `pytest` is awesome!
* Static analysis for Python does not work, pylint is slow, and hard to configure. There are tons of bugs it does not catch, and it is often wrong.
* Types annotations are useless (after all, the interpret does almost nothing with them), except maybe for documentation purposes.

I now think most of these statements are wrong, but it was what I believed at the time.

# Changing my mind

So there I was. Tools and type systems did not matter, all that matter were tests and how easy it was to write them.

All you need to do in order to have tests that you can trust and ship code without bug was to use TDD and write lots and lots of tests.

Here's a list of things that contributed to burst my bubble.


## pyflakes

I started using [pyflakes]() in [vim-ale]. pyflakes is very easy to use, requires no configuration and it's fast.

Suddenly a whole bunch of bugs disappeared: `pyflakes` is very good at finding misspelled variables or missing imports.

So maybe using TDD just to find misspelled variables or missing imports is overkill?

Of course, pyflakes does not catch other errors like calling a function with an incorrect number of arguments but still, it's quite nice to catch these errors *right after the file is saved*, instead of later when a test fails.


## pylint

I've already mentioned how [pylint can be very useful]() if you take the time to configure it properly, so I won't repeat myself here.

But still, it showed that static analysis of Python code did not have to suck after all.

## Gary Bernhardt's talk about ideology

If you haven't seen [ideology by Gary Bernhardt](https://www.destroyallsoftware.com/talks/ideology) I highly recommend it.

Excerpt:

> [This is important] mostly because it will make you better programmers, but also because it will stop you from making angry hacker news comments.

What Gary Bernhardt explains is how and why we end up saying things like *unit tests make type systems unnecessary*, and *type systems make unit tests unnecessary*, which obviously can't be both right at the same time ...

## Javascript and flow

Then there was this time when I had to make a refactoring I a Javascript project.

There were *no tests at all*, and adding them would have been pretty challenging.

But there were [flow]() annotations everywhere. Even if the errors weren't always easy to understand and even sometimes misleading, that helped a lot to build confidence that I was not breaking everything.

So adding type annotations to a language that had a very weak type system maybe was not a waste of time.

## rust

That was the last nail in the coffin. I start re-writing a Python project in rust, and suddenly all this stuff about "if it compiles, it works", and "types system makes unit tests unnecessary* finaly started to make sense.

Here's what I learned writing rust:

* Specify types is easy: all you need to annotate are function parameters and return values, and everything else is inferred by the compiler.
* Error messages and warning almost always indicate a bug or an inefficient way of doing things.
* Types can actually help you!

Let me give you a few examples:

* Anything that can fail returns a *type* (like `Option` or `Result`) that forces you to handle errors. Compare this to using exceptions or return values in other languages...
* You can't copy something unless implements the `Copy` trait.
* The `Send` and `Sync` traits define how you can use a type across threads.
* and more!

In the mean time, using TDD with rust is enjoyable. I even wrote a test to make sure a certain bug would be caught *at compile time*.

That's when I completly changed my mind: Type system did not have to suck, they could be very useful, and you could combined them with tests and get the best of two worlds.

So, here's how a "I don't need no stinkin' types" kind of guy decided to give `mypy` a try.

# Trying mypy

I wanted to see what it would look like to use `mypy` on a "real" Python project.

I decided to use `mypy` on a medium-sized project. If it was too small, I would not have enough data, and if it was too big the experiment would take too long.

So I used [tsrc]().

## How mypy works

You can use mypy in a loop:

* Start by annotating a few functions.
* Run `mypy` on your source code.
* If it detects some errors, either fix the annotations on the code.
* Back to step one

You can install `mypy` with `pip`.

I suggest you use it like this:

```
mypy --ignore-missing-imports --strict-optional .
```
