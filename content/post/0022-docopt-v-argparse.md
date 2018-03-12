---
authors: [dmerej]
slug: "docopt-v-argparse"
date: 2016-09-24T13:53:16+02:00
description: ""
draft: false
tags: ["python"]
title: docopt v argparse
---

Say you have a program named `foo` that is supposed to be used from the command
line, written in Python.

It provides lots of various features, so you decide to group them into
subcommands, like `git` or `mercurial` does for instance.

So your program can be called in the following ways:

```console
$ foo bar --baz --num-jobs=4
runs bar(baz=True, num_jobs=4)

$ foo read file.in --verbose
runs read("file.in", verbose=True)
```

Assuming you are using Python for this, which library should you use to
implement command line parsing?

<!--more-->




## An history of command line parsing in Python

### getopt

Back in the old days, the answer was
[getopt](https://docs.python.org/3/library/getopt.html)

Basically, you would call the `getopt()` function with some
weird string, like this:


```python
"""
Usage: foo [options]

Options:

  -h, --help           Display this help message
  -o, --output <PATH>  Output path
  -v,--verbose         Be verbose

"""

import sys
import getopt

def usage():
    print(__doc__)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help", "output="])
    except getopt.GetoptError as err:
        # print help information and exit:
        sys.exit(err)  # will print something like "option -a not recognized"

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-o", "--output"):
          ...
```


Here `ho:v` means you recognize the short options `-h`, `-o` and `-v`, and
the colon after the `o` means that `-o` must be followed by an argument
(so `foo -o -v` does not work, but `foo -o foo.out` does)
Note that you have to use a list of strings to have long options recognized too.
(Here `-h` and `--help` will have the same meaning)

Note the call to the `usage()` function. The *usage* of a command line program
is simply a string that describes how the program should be called.

Also note how you specify `-o,--output` **three** times: once in the docstring, once
it the `getopt()` call and finally once in the `main()` function.


### optparse

Then came [optparse](https://docs.python.org/3/library/optparse.html).

The idea was to get rid of the weird syntax to define long and short options,
and also to generate the help message and usage automatically.

To use `optparse` you create a *parser*, then call the `add_option` method for
each pair of long and short options you want to support.

Then you invoke the `parse_args()` method and it returns a tuple of two items:

The first item is a class (`optparse.Values`) that contains the values of the
options as attributes.

The second item is simply the list of positional arguments.

Note the difference between *options* and *arguments* here.

When using `optparse`, everything that is optional starts with a dash (`-`), and
is called an *option*, and everything that is required simply comes after all
the options and is called a *positional argument*, or *argument* for short.

There's no way to have "optional arguments" or "required options".

The `optparse` authors explain why they choose to enforce this behavior in the
documentation:

* [What are options for](
  https://docs.python.org/3/library/optparse.html#what-are-options-for)
* [What are positional arguments for](
  https://docs.python.org/3/library/optparse.html#what-are-positional-arguments-for)

It contains some interesting points about command line API design, so I suggest
you read it, even if you won't be using `optparse`.

By default, the attribute name of the parsed option will be computed from
its long form.

`--foo-bar=42` gives `opts.foo_bar = 42`.

But you can use `add_option("--input", dest="input_file"`) to override the name
of the attribute.

If the option does not take an argument, its parsed value will be a boolean,
and you can use `action="store_true"` or `action="store_false"`.
You can set its default value by calling `parser.set_defaults()`.

So, if you have a `foo` program that takes a required input file as argument,
and an output file as an option, you'll have to write something like:


```python
parser = OptionParser()
parser.add_option("-o", "--output", help="path to the output file")

opts, args = parser.parse_args()

if len(args) != 1:
    sys.exit("Missing one required argument")

input_file = args[0]

if opts.output:
    output_file = opts.output
else:
    output_file = input_file + ".out"
```

`optparse` has a lot of nice features:

* you don't have to write the usage or the help message yourself, it's generated
  automatically

* you can provide default values and types for your options

* you can group them together

* and so on ...

### argparse

[argparse](https://docs.python.org/3/howto/argparse.html) is a direct successor
of `optparse`.

The idea is to be more flexible that `optparse` and allowing to have "optional
arguments" and "required options", because, let's face it, sometimes it's really
convenient. For instance, for a dangerous operation, you may want the `--force`
option to be required :P

Anyway, `argparse` uses the same API that `optparse`, except that:

* `add_option` becomes `add_argument` and can be used both for *options* and
  *positional arguments*

* `parse_args` returns only one item (an `argparse.Namespace` instance) for
  the values of both the options and the positional arguments.

Porting from `optparse` to `argparse` is thus quite easy. For instance, the
previous example becomes:

```python
parser = ArgumentParser()
# it's an option because it starts with a dash:
parser.add_argument("-o", "--output", help="path to the output file")
# it's a *required* positional argument
parser.add_argument("input", dest="input_file")

args = parser.parse_args()

input_file = args.input_file

if args.output:
    output_file = args.output
else:
    output_file = input_file + ".out"
```

But you can have optional positional arguments, by using
`add_argument("foo", nargs="?")`, or required options, with
`add_argument("--force", action="store_true", required=True)`

Also, `argparse` supports what are called *subparsers*, which means you can have
complex API that runs different *commands* depending on the first argument. You
do this by calling `parser.add_subparsers()`:

```python
parser = argparse.ArgumentParser()
action_parsers = parser.add_subparsers(title="available actions")
bar_parser = action_parsers.add_parser("bar")
...
read_parser = action_parsers.add_parser("read")
...

```

This makes it possible to implement the example we started with:

```console
$ foo bar --baz --num-jobs=4

$ foo read file.in --verbose
```

A nifty hack is to use `set_defaults()` to dispatch the code after
parsing, like this:

```python
bar_parser.set_defaults(action="do_bar")
...
read_parser.set_defaults(action="do_read")
...

if args.action == "do_bar":
    ...
elif args.action == "do_read":
    ...
```


By the way, `argparse` started its life as a standalone third-party library, but
is now part of Python standard library since Python 2.7.

The official Python documentation for `getopt` and `optparse` both suggest to
use `argparse` instead.

### docopt

`docopt` came with a quite interesting new idea. What if, instead of generating
the help message automatically, we *parsed* directly the usage string?

After all, the string usage does have a pretty normalized format.
(It's even part of the "IEE Std 1003.1" standard, also knows as ... POSIX)[^1]

Instead of writing tons of boring boilerplate (instantiate the
parser, call `add_argument` a bunch of times, then `parse_args`),
what if you could just call a function using the usage string?

This is how you use `docopt`:

```python
"""
Usage:
  foo bar [--baz] [--num-jobs=<jobs>]
  foo read <input_file> [--verbose]

Options:
  --baz              Do some baz stuff
  --verbose          Be verbose
  --num-jobs=<jobs>  number of jobs [default: 1]

"""

import docopt

opts = docopt.docopt(__doc__)
print(opts)
```

Note that the return value of `docopt` is a simple Python dictionary.

The keys will be `'--baz'`, `'baz'`, or `'<baz>'` depending on the context,
and the values will always be strings, except when a subcommand is used.

So for instance you would have:

```
$ foo bar --num-jobs=42
{'--baz': False,
 '--num-jobs': '42',
 '--verbose': False,
 '<input_file>': None,
 'bar': True,
 'read': False}
% foo read input.txt
{'--baz': False,
 '--num-jobs': '1',
 '--verbose': False,
 '<input_file>': 'input.txt',
 'bar': False,
 'read': True}
```



## docopt v argparse

OK, so by now it should be pretty clear your best option is between `argparse`
and `docopt`

Note: there's also other projects like [clik](http://click.pocoo.org) that do
things differently, but:

* I never used it.
* I've been told [not to use it](http://xion.io/post/programming/python-dont-use-click.html)
* This article is already quite long ...

### Where docopt is better

#### Shorter code

Kind of obvious, right? All you have to do is import `docopt` and call
`docopt.docopt()` with the usage string.

#### Abide PEP

The [PEP 257](https://www.python.org/dev/peps/pep-0257) says:

> The docstring of a script (a stand-alone program) should be usable as its
> "usage" message, printed when the script is invoked with incorrect or missing
> arguments (or perhaps with a "-h" option, for "help"). Such a docstring should
> document the script's function and command line syntax, environment variables,
> and files. Usage messages can be fairly elaborate (several screens full) and
> should be sufficient for a new user to use the command properly, as well as a
> complete quick reference to all options and arguments for the sophisticated
> user.

`docopt` is perfect for this.


#### Full control of the \--help output

You can do this with `argparse` of course, but doing so is not trivial.
You have to implement an `argparse` "formatter class", and the names are ugly:

```
argparse.RawDescriptionHelpFormatter
argparse.RawTextHelpFormatter
argparse.ArgumentDefaultsHelpFormatter
argparse.MetavarTypeHelpFormatter
```

Ugh.

You can also prevent `argparse` from generating the help message automatically,
but then you have to re-implement handling `-h,--help` yourself.

#### Arbitrary conditions

```
Usage: my_program (--either-this <and-that> | <or-this>)
```

There isn't any way to do this directly with argparse.

You'll have to do it manually, like so:

```python
parser = argparse.ArgumentParser()
parser.add_argument("--either-this")
parser.add_argument("or_this", nargs="?")

args = args.parse_args():
if not any((args.either_this, args.or_this)):
    sys.exit("...")
```

#### Grouping exclusive options

With `docopt`:

```
Usage: foo go (--up | --down)
```

With `argparse`, you must use `add_mutually_exclusive_group()`
which is quite verbose ...

#### Maintainability

If you configure your `argparse.ArgumentParser` from several portions of your
code, you risk defining the same option twice, which will lead to this kind of
errors:

```
argparse.ArgumentError: argument -f/--format: conflicting option string: -f
```

and this gets old fast ...

#### Available for many languages

Although the reference implementation of `docopt` is in Python, the library has
been ported to quite a few languages.

The official list is [on github](https://github.com/docopt/)

### Where argparse is better

#### In the standard library

Actually, this has both pros and cons.

* Pros: you don't have to install anything, it will just work with your existing
  Python installation.
* Cons: since it's part of the standard library, you'll have to wait for a new
  Python release to get bug fixes or new features.

#### No DSL

`docopt` is able to do its magic because it uses a DSL
(domain specific language)

That's why you only need a few lines of code to use it, because the information
you need is parsed from an other language, dedicated to this task.

Quite ironically, this is the same approach used by `getopt`. The weird
`"ho:v"` string is _also_ a DSL ...

But using a DSL comes with a few cons:

For instance,  you need _2_ spaces between the option name and its description
for `docopt` to work:

```
foo

  --this-is-long Long description
  --short        Do it short
```

It's hard to see where the problem is here ...


Also, if `docopt` cannot parse your usage string, you'll get a cryptic error
message with no clue about what line is wrong:


```Python
"""
Usage:
  naval_fate ship new <name>...
  naval_fate ship <name> move <x> <y> [--speed=<kn>]
  naval_fate mine (set|remove <x> <y> [--moored|--drifting]
  naval_fate ship shoot <x> <y>
"""


from docopt import docopt
opts = docopt(__doc__)
```

```console
$ python naval_fate.py

docopt.DocoptLanguageError: unmatched '('
```

That's what you get when creating a new language: you have to take care of many
subtle details and problems that comes with it...

See [an article from ESR](http://esr.ibiblio.org/?p=7032) for some discussion
around this topic.

But this is a bit philosophical, let's get to more concrete stuff.


#### Error messages


`docopt` will *always* print the usage if it can't parse the command line, with
no explanation.

`argparse` will generate much more information:

```console
$ naval_fate move
invalid choice: 'move' (choose from 'ship', 'mine')
$ naval_fate ship new
the following arguments are required: names
$ naval_fate ship move bounty 5 fortytwo
argument y: invalid float value: 'fortytwo'
```

There's a [Pull Request](https://github.com/docopt/docopt/pull/63) to fix this,
though.

#### Options that only make sense for one operating system

Yes, this is a contrived example:

```Python
if os.name == "nt":
    parser.add_argument("--on-mingw")
```

Still, you get the idea: since you're using Python to build your parser, you
have access to the full features of the language, instead of being constrained
by the DSL.


#### Naming

I really like the fact I have a two possible "names" : one for command line API,
and an other one for the attribute of the returned value.


For instance, here is a pattern I often use:

```python
def do_foo(raises=True):
    ok = try_something()
    if not ok and raises:
        raise FooFailed()
```

Using `argparse`, I can do:

```python
parser.add_argument("--ignore-errors", dest="raises")
args = parser.parse_args()
do_foo(raises=args.raises) # I really don't care what the flag is called here
                           # for all I know, it could be --i-know-what-i-am-doing

```

With `docopt`, I would have to write:

```python
opts = docopt.docopt(__doc__)
do_foo(raises=opts["--ignore-errors"])
```

which I find less readable, but maybe it's a matter of taste.

An other example is when you need a `--no-foo` option.

I prefer using:

```python
parser.add_argument("--no-foo", dest="foo", action="store_false")
parser.set_defaults(foo=True)
...
if args.foo:
   ...
```

rather than `if not opts["--no-foo"]:`


#### Types

With `docopt`, all you get is a dictionary with strings as keys and values.
(And sometimes booleans when you have subparsers)

With argparse, you can force values to be integers, floats, existing files, or
even your own type.

For instance:

```python
def valid_filename(value)
    if value in [".", ".."]:
        raise Error("Invalid name: %s" % value)

    bad_chars = r'<>:"/\|?*'
    for bad_char in bad_chars:
        if bad_char in value:
            mess  = "Invalid name: '%s'\n" % value
            mess += "A valid name should not contain any "
            mess += "of the following chars:\n"
            mess += " ".join(bad_chars)
            raise Error(mess)
    return value

parser.add_option("-o", "--output", type=valid_filename)
```

`docopt` documentation suggest you use an other library like
[schema](https://pypi.python.org/pypi/schema) for this, but it seems a bit
overkill to me...


#### Computing return value

Here we assume that the "obvious" set of ingredients is eggs with spam.
So you want that to be the default, but still allow the user to change the list.

With `argparse` it's quite easy:


```python
parser.add_argument("--with-sugar", action="store_const",
                    dest="ingredients", const=["spam", "eggs", "sugar"])

parser.add_argument("--without-spam", action="store_const",
                    dest="ingredients", const=["eggs"])


parser.set_defaults(ingredients=["spam", "eggs"])
```

It's doable with `docopt` of course, but there's a chance you'll get it wrong
if you have to juggle with `opts["--with-sugar"]` and `opts["--without-spam"]`
yourself.

#### Custom actions

Sometimes you will need to call a custom function when a flag is present. You'll
need to write a class that inherits from `argparse.Action`, it's a bit painful
but doable.


#### Plug-ins

If you have "plug-ins" that can augment the command-line API, all you have to do
is pass the `parser` object around and let your plug-ins call `add_argument` or
what not on it.

With `docopt` you'll have to use something like
[docopt-dispatch](https://github.com/keleshev/docopt-dispatch) which is still
experimental.


#### Other configuration sources


Here's an example where we make it possible to use environment variables
starting with `FOO_` to control the behavior of the program:



```python
parser = argparse.ArgumentParser()
parser.add_argument("--bar")
env_dict = dict((k.lower()[4:], v)
            for (k, v) in os.environ.items()
            if k.startswith("FOO_"))
env_ns = types.SimpleNamespace(**env_dict)

args = parser.parse_args(namespace=env_ns)

```

Note how we just have to build a *namespace* [^2] that we then forward to the
`parse_args` call.

`docopt` authors suggest you can similarly use a configuration file
in [one of the examples](
https://github.com/docopt/docopt/blob/master/examples/config_file_example.py),
but note how:

* You have to implement the "merge" of the various dictionaries yourself
* You still need to preserve the `--` prefix for the keys, which means you're
  going to have a hard time using a YAML config file for instance ...


## The "docopt challenge"

`docopt` authors have setup a [challenge web
page](http://challenge.docopt.org/).

They ask you to write a program that has the following API:

```
Usage:
  naval_fate ship new <name>...
  naval_fate ship <name> move <x> <y> [--speed=<kn>]
  naval_fate ship shoot <x> <y>
  naval_fate mine (set|remove) <x> <y> [--moored|--drifting]
  naval_fate -h | --help
  naval_fate --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --speed=<kn>  Speed in knots [default: 10].
  --moored      Moored (anchored) mine.
  --drifting    Drifting mine.
```

Well, I took the challenge using `argparse` and the result is available
[on github](https://github.com/dmerejkowsky/docopt-challenge).

In the [README](
https://github.com/dmerejkowsky/docopt-challenge/blob/master/README.md)
I talk more about why `argparse` may be a better choice for this particular
example.

Go read it, it's complementary to this article.

There's a bit of duplication, and I apologize for that, but it was hard to
avoid.


## Conclusion


So, what library should I be using?

The answer, as always, is "it depends".

I think using `docopt` is fine for quick little scripts when you don't have many
validation to do and don't mind having all the configuration of the parser in
just one place. So typically, _not_ the "naval_fate" example promoted by
`docopt`.
It may also be a good idea for languages other than Python that lack a good
command line parsing library.

But for big projects with lots of subcommands, written in Python, using
`argparse` may be a better idea, especially if you need to do advanced stuff
for your parsing, like configuring common options in one function, allow
plug-ins to change the command line API, and so on ...


## Feedback

As always, feedback is welcomed.

See [the dedicated page]({{< ref "pages/feedback.md" >}}) on how to reach me.

Thank you for reading thus far, see you next time!


_Update_: seems like `docopt` is no longer maintained (no release since 2014),
and that `click` "won the war". I don't know enough about `click`, but I may
have a look at it later and post the results on this blog one day ...

[^1]: Stolen from the [Python UK 2012 conference on docopt](https://www.youtube.com/watch?v=pXhcPJK5cMc)

[^2]: We're using [types.SimpleNamespace](https://docs.python.org/3/library/types.html#types.SimpleNamespace) which is available since Python 3.3
