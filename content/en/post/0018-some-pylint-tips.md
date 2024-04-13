---
authors: [dmerej]
slug: "some-pylint-tips"
date: "2016-07-23T17:49:04+02:00"
description: ""
draft: false
tags: ["python"]
title: "Some pylint tips"
---

I've been using [pylint](https://www.pylint.org) for quite some time now, so
today I'd like to share a few tips with you.

*Update: Itamar Turner-Trauring also wrote a nice article about pylint,
you should read it too:*
[Why Pylint is both useful and unusable, and how you can actually use it](
https://codewithoutrules.com/2016/10/19/pylint/)

<!--more-->

## What is pylint?

It's a static analyzer for Python code.
"Static" means that it won't execute your code, it will just parse it to find
mistakes or things that do not respect a given coding style.

Pylint is capable of emitting very interesting warnings.

Here are some examples:

```python
def foo(bar, baz):
    pass

foo(42)
```

<cite>
No value for argument 'baz' in function call
(no-value-for-parameter)
</cite>

```python

class MyThread(threading.Thread):
    def __init__(self, name):
        self.name = name

    def run(self):
        ...


my_thread = MyThread()
my_thread.start()
```
<cite>
__init__ method from base class 'Thread' is not called (super-init-not-called)
</cite>

This is nice because it saves you a fatal assertion at runtime:
```text
AssertionError: Thread.__init__() not called
```

## Fixing pylint output

By default, pylint is _very_ verbose:

```text
$ pylint my_module.py
No config file found, using default configuration
************* Module my_module
C:  1, 0: Missing module docstring (missing-docstring)
...

Report
======
8 statements analysed.

Statistics by type
------------------

+---------+-------+-----------+-----------+------------+---------+
|type     |number |old number |difference |%documented |%badname |
+=========+=======+===========+===========+============+=========+
|module   |1      |1          |=          |0.00        |100.00   |
+---------+-------+-----------+-----------+------------+---------+
...
+---------+-------+-----------+-----------+------------+---------+


Raw metrics
-----------

...

Messages by category
--------------------

+-----------+-------+---------+-----------+
|type       |number |previous |difference |
+===========+=======+=========+===========+
|convention |3      |3        |=          |

...

+-----------+-------+---------+-----------+
|error      |1      |1        |=          |
+-----------+-------+---------+-----------+


Global evaluation
-----------------
Your code has been rated at -3.75/10 (previous run: 1.43/10, -5.18)
```


Let's fix that!

The goal is to have no output at all when everything is fine,
only have the errors if something is wrong, and make sure
output of `pylint` can then be used by an other program
if required. [^1]

### Get rid of "No config file found, using default configuration"

Just go to the root of your project and run:

```console
$ pylint --generate-rcfile > pylintrc
```

### More readable output

Edit the `pylintrc` file to have:

```ini
[REPORTS]

output-format=parseable
```

That way you'll get a more standard output, with the
file name, a colon, the line number and the error message:

```text
my_module.py:11: [C0103(invalid-name), ] Invalid constant name "my_thread"
```

This is useful if you want to run `pylint` from your editor and quickly
jump to the lines that contains errors.

### Get rid of the useless stuff

You don't really care about all the stats, so let's just disable everything:

```ini
[REPORTS]

reports = no
```

There! Now we only get only the warning or error messages,
except there's a big line to separate the modules:

```text
************* Module my_module
my_module.py:4: [W0231(super-init-not-called), MyThread.__init__] __init__ method from base
                class 'Thread' is not called
************* Module other_stuff
other_stuff.py:5: [W0311(bad-indentation), ] Bad indentation. Found 3 spaces, expected 4
```

## Correcting false positives

Sometimes `pylint` thinks there's a problem in your code even though it's
perfectly fine.

Here's an example using the excellent [path.py](
https://pythonhosted.org/path.py/) library:

```python
my_path = path.Path(".").abspath()
my_path.joinpath("foo")
```
<cite>
my_module.py:5: [E1120(no-value-for-parameter), main] No value for argument
'first' in unbound method call
</cite>

If you take a look, it seems that `pylint` gets confused by upstream
code:

```python
class multimethod(object):
    """
    Acts like a classmethod when invoked from the class and like an
    instancemethod when invoked from the instance.
    """
    ...


class Path():
    ...

    @multimethod
    def joinpath(cls, first, *others):
        if not isinstance(first, cls):
            first = cls(first)
        return first._next_class(first.module.join(first, *others))
```

It's some dark magic (yeah Python) to make sure you can use both:

```python
path_1 = my_path.joinpath("bar")
path_2 = path.Path.joinpath(my_path, "bar")
```

and `pylint` only "gets" the second usage...

Here the solution is to use a "pragma" to tell `pylint` that the code is fine

```python
my_path = path.Path(".").abspath()
# pylint: disable=no-value-for-parameter
a_path = my_path.joinpath("foo")
```

But if you do that, you'll get:

<cite>
my_module.py:5: [I0011(locally-disabled), ] Locally disabling no-value-for-parameter (E1120)
</cite>

The solution is to disable warnings about disabled warnings (so meta):

```ini
[MESSAGES CONTROL]

disable=reduce-builtin,dict-iter-method,reload-builtin, ... ,locally-disabled
```

## Freezing pylint version

If you're like me, you probably have a `dev-requirements.txt` containing a line
about `pylint` in order to use in a `virtualenv`.

It's also possible you're using [buildout](http://www.buildout.org/en/latest).

But anyway, I highly recommend you have a separate installation of `pylint` just
for your project, isolated from the rest of your system.

The fact is that `pylint` depends on `astroid`, and both projects are constantly
evolving.

So if you're not careful, you may end up upgrading `astroid` or `pylint` and
suddenly some false positives will get fixed, and some other will appear.

So to make sure this does not happen, always freeze `pylint` and `astroid`
version numbers, like so:

```text
pylint==1.5.5
astroid==1.4.7
```

(you can use `pip freeze` to see the version of all the packages in your
`virtualenv`)

## Running pylint

To run `pylint`, you have to give it a list of packages or modules do check
on the command line.

For instance, let's assume your sources look like this:

```text
src
  pylintrc
  bar.py
  spam
     __init__.py
     eggs.py
```


Then you have to call `pylint` like this:

```console
$ cd src
$ pylint bar.py spam
```

You may try to run `pylint .` or just `pylint` but it won't work :/

So this means that anytime you add a package or a new module, you have to change
the way you call `pylint`.

This is rather annoying, that's why I suggest you use [invoke](http://www.pyinvoke.org).

Write a `tasks.py` file looking like:

```python
import path
import invoke

def get_pylint_args():
    top_path = path.Path(".")
    top_dirs = top_path.dirs()
    for top_dir in top_dirs:
        if top_dir.joinpath("__init__.py").exists():
            yield top_dir
    yield from (x for x in top_path.files("*.py"))


@invoke.task
def pylint():
    invoke.run("pylint " + " ".join(get_pylint_args()), echo=True)

```

And then you just have to use:

```console
$ invoke pylint
```


### Speeding up pylint


`pylint` also knows how to use multiple jobs so that it runs faster.

Since you are already using `tasks.py`, you can specify the number of
jobs to use in a cross-platform way easily:

```python
import multiprocessing


def get_pylint_args():
    ...

    num_cpus = multiprocessing.cpu_count()
    yield "-j%i" % num_cpus
```

## Shorter version

You can also _not_ do all of the above and just fire up `pylint` like so:

```
$ pylint -E *.py
```

It will only show errors, (`-E` is short for `--errors-only`), and will
have a good enough output.

* Pros: you don't have to write any `pylintrc` file
* Cons: you may hide serious bugs




That's all for today, see you next time!



[^1]: Congrats if you noticed this is part of the [Unix philosophy](https://en.wikipedia.org/wiki/Unix_philosophy)
