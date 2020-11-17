---
authors: [dmerej]
slug: else-after-return-yea-or-nay
date: "2018-07-12T15:38:15.003805+00:00"
draft: false
title: "Else after return: yea or nay?"
tags: [python]
summary: "Should you fix your code to remove unnecessary else after a return statement?"
---


# Introduction

As you may know, I use [pylint](https://www.pylint.org/) for most of my Python projects. [^1]

A few weeks ago, I upgraded pylint and a new warning appeared. This tends to happen when you have a pretty large code base: new checks are added to pylint all the time, so new warnings are bound to show up.

Here's a minimal example of the kind of code that triggered the new warning:

```python
def foo():
    if bar:
        return baz
    else:
        return qux
```


```
$ pylint foo.py
...
Unnecessary "else" after "return" (no-else-return)
```

Indeed, the code after the first return will never execute if `bar` is true, so there's no need for the `else`.

In other words, the code should be written like this:

```python
def foo():
    if bar:
        return baz
    return qux
```

Well, the code is shorter. But is it *better*?


# The problem

If you think about it, the question about whether the code is *better* in the first form (let's call it *explicit else*) or in the second form (let's call it *implicit else*) is hard to answer because you have no clue about the *meaning* of the `foo` function, or the `bar`, `baz` and `qux` variables.

So let's try to come up with better examples.

# Guard clauses

Sometimes you'll find code written this way:

```python
def try_something():
    if precondition():
         result = compute_something()
         return result
    else:
        display_error()
        return None
```

In other words, you are trying to do something but that's only possible if a condition is true. If the condition is false, you need to display an error.

The `else` is explicit here.

The version with an implicit `else` looks like this:

```python
def try_something():
    if precondition():
         result = compute_something()
         return result
    display_error()
    return None
```

So far, it's not very clear what version is better.

Note there's a third way to write the same code, by using `if not precondition()` instead:

```python
# Implicit else, inverted condition
def try_something():
    if not precondition():
        display_error()
        return None

    result = compute_something()
    return result
```

Now, watch what happens when we add several preconditions:

```python
# Explicit else
def try_something():
    if precondition_one():
        if precondition_two():
            result = compute_something()
            return result
        else:
            display_error_two()
            return
    else:
        display_error_one()
```

```python
# Implicit else, inverted condition
def try_something():

    if not precondition_one():
        display_error_one()
        return

    if not precondition_two():
        display_error_two()
        return

    result = compute_something()
    return result
```

I hope you'll agree the second version is better.

There's one less level of indentation, and the line that *displays* the error is right after the line that *checks* for the error.

Clear win for the *implicit else* here.

# Symmetric conditions

Let's take an other example.

Suppose you are writing a script that will check all the links in documentation written as a set of HTML pages.

You've got a list of all the possible pages, and then you need to check both *internal links* (with a `href` looking  like
`../other-page`) and *external links* like (with a `href` like `http://example.com`).

Let's take a look at the two variants:

```python
# Implicit else
def check_link(link) -> bool:
    if is_internal_link(link):
        return check_internal_link(link)
    return check_external_link(link)
```

```python
# Explicit else
def check_link(link) -> bool:
    if is_internal_link(link):
        return check_internal_link(link)
    else:
        return check_external_link(link)
```

This time, I hope you'll agree the explicit else is better.

There are two things to be done, and visually they are at them at the same level of indentation.

The symmetry between the type of the link and the check that needs to be done is preserved.

We could say that the algorithm I've described as text in the last paragraph is better *expressed* in the second version.

# Conclusion

Pylint is a great tool, but be careful before deciding whether you want to follow its refactoring pieces of advice.

Second, make sure your code is *easy to read* and *reveal your intention*. Conciseness is not the only factor here.

Last, be careful with code samples that are too abstract :)

Cheers!


[^1]: I already blogged about this in [Some pylint tips]({{< ref "/post/0018-some-pylint-tips.md" >}}) and [How I lint my Python]({{< ref "/post/0037-how-i-lint-my-python.md" >}}).
