---
slug: symlinks-made-easier
date: 2017-01-31T19:25:05.009506+00:00
draft: false
title: symlinks made easier
tags: ["python"]
---

For years I've been struggling with the `ln` command.

I never could remember how to use it, mixing the order of the parameters,
and the man page did not help.

```console
$ man ln

SYNOPSYS
      ln [OPTION]... [-T] TARGET LINK_NAME   (1st form)
      ln [OPTION]... TARGET                  (2nd form)
      ln [OPTION]... TARGET... DIRECTORY     (3rd form)
      ln [OPTION]... -t DIRECTORY TARGET...  (4th form)
```

So I thought, why not write a small wrapper around it?

<!--more-->

## Introduction

A `symlink` is a special file that "points" to an other.

I've seen it used frequently in the `download` folder of servers:

```console
$ ls -l  download
0.1
0.2
0.3
latest -> 0.3
```

Thus, when you go to `http://example.com/latest` you always get the latest
release, and to deploy a new release, one can:

* Upload the `0.4` release
* Re-create the `latest` symlink

Which are "atomic" operations, meaning:

* The filesystem is always in a coherent state
* It's easy to revert to a previous release if necessary.

So, my mental image of a link is an arrow, going from one filename to an other:


```text
a -> b  (link from a to b)
or
a <- b  (link to a from b)
```

But `a` and `b` can be in any order.

## Choosing parameter names

The first thing I did was to use variable names that I could understand.

I choose the names `from` and `to`:

```python
def ln(*, from_, to):
    os.symlink(to, from_)
```

I'm using Python3 syntax to make sure that *both* `from` and `to` have to be
explicitly specified when calling the function.

I also use `from_` with an underscore at the end because `from` is a Python
keyword.

Note that in Python2, I would have written
```python
def ln(from_=None, to=None):
    ...
```

but then nothing would have prevented people (including me),  from using `ln(a,
b)`, which is exactly what I want to avoid.

I also wrote a test which forced me to get the order of the `os.symlink()` call
right.

Because of course, I _also_ don't know how to call `os.symlink()`,
arguments are named `src` and `dest`, and those names are as meaningless to me
as the names in the `ln` man page ...

## Coming up with a Command Line Interface

### First attempt

My first idea was to have two ways to call my `ln` wrapper, with names that
remembered me about the direction of the arrow.

So something like `ln-lt` (for the lesser than sign, aka&nbsp;`<`) and `ln-gt`
(for the greater than sign, aka&nbsp;`>`).

But that was confusing, and the code was not very readable:

```python
def main_lt(a, b):
    _main("<", a, b)

def main_gt(a, b):
    _main(">", a, b)

def _main(direction, a, b):
    from_ = a
    to = b
    if direction == "<":
        # going the other way, need to swap:
        from_, to = to, from_
```



### Second attempt

And then I realized I could just use the names `first` and `second`, display the
two possibilities and let the user (me) choose interactively:

```python
def main(first, second):
    print("1.", first,  "->", second)
    print("2.", second, "->", first)

    answer = input("Which one? ")
    if answer == "1":
        from_ = first
        to = args.second
    elif answer == "2":
        to = first
        from_ = second
    else:
        sys.exit("Please choose between 1. and 2.")
```

## Going Interactive

Since I was already interacting with the user, the next logical step was to
handle the case where the symlink already exists.

Normally, when I get an error from `ln` looking like:

```console
$ ln -s bar foo
ln: failed to create symbolic link 'foo': File exists
```

my first instinct is to run `ls -l` to check that I'm actually overwriting a
symbolic link, (which is easy to revert) and not a regular file (which could
lead to data loss).

Then I use `rm foo`, which prompts me for a confirmation (because I've aliased
`rm` to `rm -i` [^1]), or I re-run the `ln` command with the `--force` switch.

I realize I could avoid doing all that with just a few more lines of code:

```python
if os.path.islink(from_):
    dest = os.readlink(from_)
    message = "{} -> {} already exists. Overwrite? (Y/n) "
    message = message.format(from_, dest)
    answer = input(message)
    if answer == "n":
        sys.exit(1)
    else:
        os.remove(from_)

if os.path.exists(from_) and not os.path.islink(from_):
    message = "Error: {} already exists and is not a symlink"
    sys.exit(message.format(from_))
```

## Releasing to the world

After that, I created a [github repo](https://github.com/dmerejkowsky/ln.py),
made a [release on pip](https://pypi.python.org/pypi/ln.py) and created a quick
[demo on asciinema](https://asciinema.org/a/101084)
because that's what the cool kids seem to do nowadays.

I don't really expect contributions because the code does everything I need,
and I don't really expect you to want to use it.

(Maybe you've managed to remember the order of arguments because it's `EXISTING
NEW`, the same order as `cp`, or maybe you have a different mental image of
symlinks, or you don't use the command line at all, and nothing is wrong with
you).

Nevertheless, I though it would be interesting to show an example of how you can
tweak your tools to have an API and UI that matches how *your* brain works.

Plus it's a nice way to show you how Python3 is awesome :P

*Update*: someone had the same kind of idea for implementing a safer
`rm`. You can read more on [github](https://github.com/alanzchen/rm-protection)


[^1]: Old habit. This one is not likely to go away ...
