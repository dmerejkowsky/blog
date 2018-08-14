---
authors: [dmerej]
slug: hello-flake8
date: 2018-08-13T14:12:44.006921+00:00
draft: false
title: "Hello flake8"
tags: [python]
summary: flake8 is awesome and has a bright future ahead
---

# Introduction

In my [last article]({{< ref "post/0079-bye-bye-pylint.md" >}}) I explained why I decided to no longer use pylint.

In a nutshell, most pylint warning are now caught by other linters, and all that's left are
some warnings.

In an [other article]({{< ref "post/0037-how-i-lint-my-python.md#putting-it-all-together" >}}) I mentioned [flake8](http://flake8.pycqa.org/en/latest/) briefly, saying that I preferred a simple bash script to drive the execution of the various linters.

I was concerned that flake8 did not include pylint (now I no longer care of course). Also, I did not like the fact that flake8 forces a specific version for all the linters it runs.

Well, I was wrong (again).

# flake8 is awesome

First off, I thought flake8 only combined the pyflakes and pycodestyle linters and nothing else. [^1]. Well, it also includes [mccabe](https://pypi.org/project/mccabe/) by default.

Also, as explained in the [FAQ](http://flake8.pycqa.org/en/latest/faq.html#why-does-flake8-use-ranges-for-its-dependencies), there are significant advantages in having the versions of the linters frozen this way.

Here are some other features I overlooked:

* You can use the `setup.cfg` file to configure all the linters flake8 knows about
* The output is consistent for all the linters
* The checks of any linter can be be disabled on any line with just a `# noqa` comment
* flake8 can also be used with plugins, and [there are a bunch of them](https://pypi.org/search/?q=flake8-) already available.

# A nice surprise

The last time I upgraded pylint, I only got one new warning. It was on a line looking like this:

```python
my_set = set([elem for elem in my_list if some_condition(elem)])
```

The intent here is to build a unique set from a list of elements that satisfy a given condition.

pylint emitted the following warning:

```
R1718: Consider using a set comprehension (consider-using-set-comprehension)
```

Indeed, the code can also be written like this, using a *set comprehension* instead:

```python
my_set = {elem for elem in my_list if some_condition(elem)}
```

Advantages:

* The code is shorter
* We no longer build a list (inside the  square brackets) just to throw it immediately afterwards
* The interpreter does not have to look up the `set()` function, so the code is faster

Well, there is already a flake8 plugin called [flake8-comprehension](https://pypi.org/project/flake8-comprehensions/) that deals with these kind of issues.

In fact, [there are a bunch of flak8 plugins](https://pypi.org/search/?q=flake8-) available!


Plus, adding a new flake8 plugin is as easy as running `pipenv install --dev <plugin nmae>` and nothing else has to change :)

# The future is bright

Itamar Turner-Trauring [^2], in the [comment section](https://dev.to/dmerejkowsky/bye-bye-pylint-4chh) on dev.to gave an interesting example:


```python
# Note: I've taken the liberty of making the code a bit less abstract
def greet(prefix, name):
    print(prefix, name)

greeters = list()
prefixes = ["Hi", "Hello", "Howdy"]
for prefix in prefixes:
    greeters.append(lambda x: greet(prefix, x))

for greeter in greeters:
    greeter("world")
```

You may think the following code would print:

```
Hi world
Hello world
Howdy world
```

but instead it prints:

```
Howdy world
Howdy world
Howdy world
```

This has to do with how the closures work in Python, and the bug is indeed caught by pylint:

```
$ pylint example.py
 W0640: Cell variable `prefix` defined in loop (cell-var-from-loop)
```


I did not find a flake8 plugin that could catch this bug right away, but I found [flake8-bugbear](https://github.com/PyCQA/flake8-bugbear), a plugin to "find likely bugs and design problems".

The plugin is which is well-written, well-tested and easy to contribute too.

I've already tried [porting some pylint warnings to  flake8-bugbear](https://github.com/PyCQA/flake8-bugbear/pull/51) and so far it has been much easier than I thought. [^3]


That means that next time I find a bug that could have been caught by inspecting the AST (which is what both flake8-bugbear and pylint do), I know how to write or contribute to a flake8 plugin in order to automatically catch it during CI.

Thus, I can slowly build a complete replacement for pylint, with just the warnings I care about, and without the configuration issues and false positives.

Bright future indeed!



[^1]: The name of the project is somewhat misleading.
[^2]: If you haven't already, you should definitively check [his blog](https://codewithoutrules.com/) and subscribe to the *Software Clown* mailing list.
[^3]: Note that the pull request was actually not merged. In reality, I started by blindly adding a new check in flake8 *before* taking a look at the whole list of flake8 plugins. The pull request got closed because it turned out the check I added was already in the `flake8-comprehensions` plugin. Sometimes you have to lie to make a better story ...
