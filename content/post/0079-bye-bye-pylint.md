---
authors: [dmerej]
slug: bye-bye-pylint
date: 2018-08-07T17:23:02.720690+00:00
draft: false
title: "Bye-bye pylint"
tags: [python]
---

I've been using [pylint](https://www.pylint.org/) for almost a decade now.

Fast-forward ten years later, and I've decided no longer use it. Read more to know why.

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

Now let's see a few problems I've encounter while using pylint.

# Pain points

## Initial setup

Initial setup of `pylint` is always a bit painful. However, if you follow [some advice]({{< ref "post/0018-some-pylint-tips.md" >}}) you can get through it.

## False negatives

A recurring issue with `pylint` is the amount of false negatives. That is, when pylint thinks something is wrong but the code is perfectly OK.
Here are a few examples:

### With attr

I like using the [attrs](http://www.attrs.org/en/stable/overview.html) library whenever I have a class that mostly contains data, like so:

```python

import attr

@attr.s
class Foo:
    bar = attr.ib()
    baz = attr.ib()
```

With just this code, I get a nice human-readable `__repr__`, a complete set of comparison methods, sensible constructors (among other things) without any boiler plate.

But when I run `pylint` on this I get:

```
foo.py:3: [R0903(too-few-public-methods), Foo] Too few public methods (0/2)
```

Pylint only sees the methods defined inside foo, and does not know about all the nice methods added by `attr`, but we use `attr` *specifically* to avoid writing all these methods.


### Pylint annotations

So if you want to keep the output of pylint usable you have to insert a specially formatted comment to tell pylint that
the following line is fine:

```python
from typing import TypeVar

# pylint: disable-msg=invalid-name
T = TypeVar('T')

```

This gets old fast, especially when every time you upgrade Pylint you get a new bunch of checks added which sometimes catch new issues, but more often than note, also trigger a bunch of new errors you much check one by one to check if it's a false positive or not.

But so far I had managed to overcome those pain points. So what changed?


# Turning the page

Two things happened:

First, I've [started using `mypy`]({{< ref "post/0071-giving-mypy-a-go.md" >}}) [^1] and a real type system.

What I found is that `mypy` can catch many of the errors `pylint` would catch, and probably more.

Also, since it uses type annotations it's both faster and more precise than pylint (because it does not have to "guess" anything).

Last but not least, it was also designed to be used *gradually*, emitting errors only when it is _sure_ there's something wrong.

Secondly, I decided to port one of my projects to Python3.7. I had to bump pylint from `1.9` to `2.1` (because older pylint versions do not support Python3.7). I got 18 new `pylint` errors, which only *one* of them being actually relevant.

It was at this moment I decided to take a step back.

# Categories

As we saw in those examples, the pylint error message contain a short name for the error (like `too-many-function-args`), and an numeric ID prefixed by a letter (`E1121`).

Each letter corresponds to a pylint *category*.

Here is a complete list:

* (_F_)atal (something prevented pylint for running normally)
* (_E_)rror (serious bug)
* (_W_)arning (not so serious issue)
* (_I_)nfo (errors like unable to parse a # pylint-disable comment)
* (_C_)onvention (coding style)
* (_R_)efactoring (code that could be written in a clearer or more Pythonic way)


Note that Fatal and Info categories are only useful when we try to understand why pylint does not behave the way it should.

# The rise of the linters

You see I realize I could use better linters (not just `mypy`) for almost every pylint category.

* Some of the *Error* messages can also be caught by `pyflakes` which is fast and produces very few false positive too.
* The *Convention* category can also be taken care of by [pycodestyle](https://pycodestyle.readthedocs.io/en/latest/).
* A few *Refactoring* warnings (but not all) can also be caught by [mccabe](https://pypi.org/project/mccabe/), which measures code complexity.

So far I've been using all theses linters in *addition* to pylint, as explained in [how I lint my Python]({{< "post/0037-how-i-lint-my-python.md" >}})

But what if I stopped using pylint altogether ?

All I would lose would be some of the *Refactoring* messages, but as we saw, many of them also cause false positive, and the most serious ones can be caught during code review.

And that's how I stopped using pylint and removed it from my CI scripts. My apologies to pylint authors and maintainers: you did a really great job all these years, but new and better tools have come up and it's time for me to move on.

# What's next

This is not the end of the story of my never-ending quest of tools to help me write better Python tools. There are  more things to be said about linting in Python, so stay tuned for the next episode ;)


[^1]:
