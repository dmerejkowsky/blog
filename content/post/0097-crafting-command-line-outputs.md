---
authors: [dmerej]
slug: crafting-command-line-outputs
date: 2019-03-25T13:55:26.357243+00:00
draft: true
title: "Crafting command line outputs"
tags: [misc]
---


I've used and wrote many command line tools. It always makes me feel happy when I come across a tools that as a nice, usable and friendly output so I always try to make the tools I write as good as possible in this regard.

Along the way, I've learned a few tricks I'd like to share with you here.

# Start with the contents

When designing command line output, start with the *contents*, not the style.
In other words, think about *what* before thinking about *how*.

Here's a few guidelines:

## Error messages

The absolute minimum your project needs is *error messages*.
Pay to those! A good error message should:

* Contain a clear summary describing what went wrong
* As many details as relevant (but not too much)
* And possibly a suggestion on how to fix the issues.

Bad example:

```
Could not open cfg file. ENOENT 2
```


Good example:

```
Error while reading config file (~/.config/foo.cfg)
Error was: No such file or directory
Please make sure the file exists and try again
```

## stdout and stderr

Speaking of error messages, note that your can choose to write text to *two* different channels (often called `stdin` and `stdout`). Use `stderr` for error messages and error messages only. People sometimes need to hide "normal" messages from your tool, but they'll need to know about those errors!

## Progress

If your tool does some lengthy work, you *have* to output something so that the user knows your tool is not suck.

The best possible progress counter contains:
* An ETA
* A progress bar
* A speed indicator

`wget` does that really well. You can also look at what `tqdm` does too.

This maybe hard to achieve, so as a lightweight alternative you can just display a counter: (`1/10`, `2/10`, ...).

But if you do so, pleas make sure the user knows *what is being counted* !

## Remove noise

Some people maybe running your tool without a terminal attached. In this case, you should remove progress bars and the like.


Also, try to remove things that are only useful when debugging (or don't display them by default).

This includes the times taken to perform a given action (unless it's useful to the end-user, like a test runner for instance). Also, don't forget that users can and will prefix their command line with `time` to get precise results if they need to.

A good way to remove noise is to completely erase the last line before writing a new one.

Here's how to do it in python:

```python
size = shutil.get_terminal_size()
print(first_message, end="\r")
do_something()
print(" " * size.columns, end="\r")  # fill up the line with blanks
                                     # so that lines don't overlap
print(second_message)
```

Of course, this only works if the user does not need to know about the whole suite of messages!


# Colors

Things to know about colors:

* Follow existing conventions, like red for errors
* Try to use them in a *consistent* way.
* On Linux and macOS, coloring is achieved by emitting certain non-printable ASCII characters (sometimes refered to as ANSI escape codes). This is fine when your program runs in a terminal, but *not* when its output is redirected to a file, for instance. Side note: you should use `sys.stdout.isatty()` or equivalent to check. `isatty()` is almost certainly in the standard library of your favorite language :)
