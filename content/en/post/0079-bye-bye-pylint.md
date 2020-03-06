---
authors: [dmerej]
slug: bye-bye-pylint
date: 2018-08-07T17:23:02.720690+00:00
draft: false
title: "Bye-bye pylint"
tags: [python]
---

I've been using [pylint](https://www.pylint.org/) for almost a decade now.

Fast-forward ten years later, and I've decided no longer use it.

Here's why.

<!--more-->


# Introduction

Let's start with an example. Consider the following, obviously incorrect code:

```python
def foo():
    ...

if __name__ == "__main__"
    foo(1, 2, 3)
```

Here's what the output of pylint might look like when you run it:

```
$ pylint foo.py
foo.py:4: [E1121(too-many-function-args), ]
  Too many positional arguments for function call
```

Now let's see a few problems I've encountered while using pylint.

# Pain points

## Initial setup

Initial setup of pylint is always a bit painful. However, if you follow [some advice]({{< ref "/post/0018-some-pylint-tips.md" >}}) you can get through it.

## False positives

A recurring issue with pylint is the amount of false positives. That is, when pylint thinks something is wrong but the code is perfectly OK.

For instance, I like using the [attrs](http://www.attrs.org/en/stable/overview.html) library whenever I have a class that mostly contains data, like so:


```python
import attr

@attr.s
class Foo:
    bar = attr.ib()
    baz = attr.ib()
```

Those few lines of code give me a nice human-readable `__repr__`, a complete set of comparison methods, sensible constructors (among other things), and without any boiler plate.

But when I run pylint on this file I get:

```
foo.py:3: [R0903(too-few-public-methods), Foo] Too few public methods (0/2)
```

Well, it's perfectly fine to require at least 2 public methods for every class you declare. Most of the time, when you have a class with just *one* public method it's better to just have a function instead, like this:

```python

# What you wrote:
class Greeter
    def __init__(self, name="world"):
        self._name = name

    def greet(self):
    print("Hello", self.name)


# What you should have written instead:
def greet(name="world"):
    print("Hello" , name)
```


But here pylint does not know about all the nice methods added "dynamically" by `attr` and wrongly assumes our design is wrong.

Thus, if you run pylint during CI and you fail the build if any error is found, you have to insert a specially formatted comment to locally disable this warning:

```python
import attr

# pylint: disable=too-few-public-methods
@attr.s
class Foo:
  ...

```

This gets old fast, especially because every time you upgrade pylint you get a new bunch of checks added. Sometimes they catch new problems in your code, but you still have to go through each and every new error to check if it's a false positive or a real issue.

But so far I had managed to overcome those pain points. So what changed?


# Turning the page

Two things happened:

First, I've [started using mypy]({{< ref "/post/0071-giving-mypy-a-go.md" >}}) and a "real" type system [^1].

What I found is that mypy can catch many of the errors pylint would catch, and probably more.

Also, since it uses type annotations mypy is both faster and more precise than pylint (because it does not have to "guess" anything).

Last but not least, mypy was also designed to be used *gradually*, emitting errors only when it is _sure_ there's something wrong.

Secondly, I decided to port one of my projects to Python3.7. I had to bump pylint from 1.9 to 2.1 (because older pylint versions do not support Python3.7), and I got 18 new pylint errors, which only *one* of them being actually relevant.

It was at this moment I decided to take a step back.

# Categories

As we saw in those examples, the pylint error messages contain a short name for the error (like `too-many-function-args`), and an numeric ID prefixed by a letter (`E1121`).

Each letter corresponds to a pylint *category*.

Here is a complete list:

* (_F_)atal (something prevented pylint from running normally)
* (_E_)rror (serious bug)
* (_W_)arning (not so serious issue)
* (_I_)nfo (errors like being unable to parse a `# pylint: disable` comment)
* (_C_)onvention (coding style)
* (_R_)efactoring (code that could be written in a clearer or more Pythonic way)


Note that *Fatal* and *Info* categories are only useful when we try to understand why pylint does not behave the way it should.

# The rise of the linters

I realized I could use other linters (not just mypy) for almost every pylint category.

* Some of the *Error* messages can also be caught by [pyflakes](https://pypi.org/project/pyflakes/) which is fast and produces very few false positive too.
* The *Convention* category can also be taken care of by [pycodestyle](https://pycodestyle.readthedocs.io/en/latest/).
* A few *Refactoring* warnings (but not all) can also be caught by [mccabe](https://pypi.org/project/mccabe/), which measures code complexity.

So far I've been using all theses linters in *addition* to pylint, as explained in [how I lint my Python]({{< ref "/post/0037-how-i-lint-my-python.md" >}})

But what if I stopped using pylint altogether?

All I would lose would be some of the *Refactoring* messages, but I assumed most of them would get caught during code review. In exchange, I could get rid of all these noisy `# pylint: disable` comments. (34 of them for about 5,000 lines of code)

And that's how I stopped using pylint and removed it from my CI scripts. My apologies to pylint authors and maintainers: you did a really great job all these years, but I now believe it's time for me to move on and use new and better tools instead.

# What's next

This is not the end of the story of my never-ending quest of tools to help me write better Python code. You can read the rest of the story in [Hello flake8]({{< ref "/post/0080-hello-flake8.md" >}}).


[^1]: By the way, at the end of  _[Giving mypy a go](https://dmerej.info/blog/post/giving-mypy-a-go/)_ I said I was curious to know if mypy would help during [a massive refactoring](https://github.com/SuperTanker/tbump/pull/24/commits/7aecba923feda081360d36892f8716045d0b1bd0). Well, it did, even better than I would have hoped!
