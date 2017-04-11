---
slug: introducing-python-cli-ui
date: 2017-04-10T19:50:46.740920+00:00
draft: true
title: Introducing python-cli-ui
---

For quite some time I've been adding a file called `ui.py` in some
of the Python projects I was working on.

Since I believe in the [rule of
three](https://blog.codinghorror.com/rule-of-three/) and I already have three
different projects using it, I've decided to share it to the world.

Feel free to take a look at the [github page](https://github.com/dmerejkowsky/python-cli-ui).

<!--more-->

# What it does

## Coloring

It's a module to write colorful command line interfaces in Python.

It's a tiny wrapper on top of `colorama`, with a (IMHO) nicer API than
[crayons](https://pypi.python.org/pypi/crayons) or
[lazyme](https://pypi.python.org/pypi/lazyme).

Here's an example:

```python
ui.info(ui.red, "Error", ui.reset, ui.bold, file_path, ui.reset, "not found")
```

This will print the word 'Error' in red, the file path in bold, and the
'not found' normally.

## Displaying enumerations

It also allows to display items of a list, taking care of
"off-by-one" errors and aligning the numbers nicely (note the
leading space for ` 1/12`)

```python
>>> months = ["January", "February", ..., "December"]
>>> for i, month in enumerate(mounths):
>>>     ui.info_count(i, 12, mount)
* ( 1/12) January
* ( 2/12) February
...
* (12/12) December
```

## Indenting

```python
>>> first_name = "John"
>>> last_name = "Doe"
>>> adress = """\
ACME Inc.
795 E Dragram
Tucson AZ 85705
USA
"""
>>> ui.info("People")
>>> ui.info(ui.tabs(1), first_name, last_name)
>>> ui.info(ui.tabs(1), "Adress:")
>>> ui.info(ui.indent(2, adress))
People:
  John Doe
  Adress:
    795 E Dragram
    Tucson AZ 85705
    USA
```


## Semantics

If you let people use color the way they want, you may end up with an
inconsistent UI.

To prevent this, the module also contains "high-level" methods such as
`info_1`, `info_2`, `info_3`, so that you can write:

```python
ui.info_1("Make some tea")

...

ui.info_2("Boiling water")

...
ui.info_3("Turning kettle on")

...
```

In the same vein, `warning`, `error` and `fatal` methods are provided for when
things go wrong. (The last one calls `sys.exit()`, hence the name)

There's also a `debug` function.

You can control the verbosity using the `CONFIG` global dictionary.

```python
ui.CONFIG['quiet'] = True

ui.info("this is some info") # won't get print
```

## Interaction

### Arbitrary string with a default

```python
>>> domain = ui.ask_string("Please enter your domain name", default="example.com")
>>> print("You chose:", domain)
> Please enter your domain name (example.com)
(nothing)
> You chose example.com

>>> domain = ui.ask_string("Please enter your domain name", default="example.com")
>>> print("You chose:", domain)
> Please enter your domain name (example.com)
foobar.com
> You chose foobar.com
```

### Boolean choice

Note how the prompt goes from `Y/n` (y uppercase), to `y/N` (n uppercase)
depending on the default value:

```python
>>> with_sugar = ui.ask_yes_no("With sugar?", default=True)
> "With sugar ? (Y/n)
n
> False

>>> with_cream = ui.ask_yes_no("With cream?", default=False)
> "With cream? (y/N)
(nothing)
> False
```

### Choice in a list

Note how the user is stuck in a loop until he enters a valid answer,
and how the first item is selected by default:

```python
>>> choices = ["apple", "orange", "banana"]
>>> answer = ui.ask_choice("Select a fruit:", choices)
> Select a fruit:
1. apple (default)
2. orange
3. banana
> foobar
Please enter a number between 1 and 3
> 4
Please enter a number between 1 and 3
> 2
>>> print(answer)
oranges
```



## Other goodies

### A timer

```python
@ui.timer("Doing foo")
def foo():
     # something that takes time

>>> foo()
... # output of the foo method
Doing foo took 3min 13s
```

Works also in a `with` statement:

```python
with ui.timer("making foobar"):
    foo()
    bar()
```

### Did you mean?


```python
>>> commands = ["install", "remove"]
>>> user_input = input()
intall
>>> ui.did_you_mean("No such command", user_input, choices)
No such command.
Did you mean: install?
```

### A pytest fixture

You can also write tests to assert that a certain message matching a regexp was
emitted.

```python
def say_hello(name):
    ui.info("Hello", name)

def test_say_hello(messages):
    say_hello("John")
    assert messages.find(r"Hello\w+John")
```

# Parting words

Well, I hope you'll find this module useful.

As explained in the [github
README](https://github.com/dmerejkowsky/python-cli-ui/blob/master/README.md)
I have no plans on making a proper `pypi` release just yet, but I'm will to
accept pull requests or any other kind of feedback :)

Cheers!
