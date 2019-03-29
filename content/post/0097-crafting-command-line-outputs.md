---
authors: [dmerej]
slug: crafting-command-line-outputs
date: 2019-03-25T13:55:26.357243+00:00
draft: false
title: "Crafting command line outputs"
tags: [misc]
---


I've used many command line tools. It always makes me feel happy when I come across a tool that has a nice, usable and friendly output. I always try to make those I create or maintain as good as possible in this regard.

Along the way, I've learned a few tricks I'd like to share with you.

<!--more-->

# Start with the contents

When designing command line output, start with the *contents*, not the style.
In other words, think about *what* to print before thinking about *how* to print it - this is helpful in a lot of other situations.

# Error messages

The absolute minimum your command line tool needs are *good error messages*.
Pay attention to those -  good error messages can go a long way in helping your users and may even save you from having to answer a bunch of bug reports! [^1]

A good error message should:

* Start with a clear summary describing what went wrong
* Contain as many details as relevant (but not too much)
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


# Standard out and standard error

Speaking of error messages, note that your can choose to write text to *two* different channels (often called `stdin` and `stdout` for short). Use `stderr` for error messages and error messages only. People sometimes need to hide "normal" messages from your tool, but they'll need to know about those errors!

# Colors

Things to know about colors:

* Use red for errors (that's about the only convention I know of which is somewhat followed by everyone).
* You can get a lot of meaning out of simple, ASCII-art decoration. Don't necessarily reach from emojis immediately 😜.
* Try to use colors in a *consistent* way. Having helper methods like `print_errror()`, `print_message ()` can help.
* On Linux and macOS, coloring is achieved by emitting certain non-printable ASCII characters (sometimes referred to as ANSI escape codes). This is fine when your program runs in a terminal, but *not* when its output is redirected to a file, for instance.
* People usually expect color activation to be controlled with a tri-state: "always", "never", or "auto". The first two are self-explanatory, but "auto" needs some explaining.
* When "auto" is set, your program should decide whether to use colors by itself. You can do so by calling `isatty(stdout)` or something equivalent.
* On Windows, coloring is achieved by using the win32 API, but the same ideas apply.
* There's probably a library near you that implements all of this. Even if it does not seem much, there's no point in re-inventing the wheel here.
* Finally, try to follow the [CLICOLORS standard](
https://bixense.com/clicolors/).

# Progress

If your comman-line tool does some lengthy work, you should output _something_  to your users so that they know your program is not stuck.

The best possible progress indicator contains:

* An ETA
* A progress bar
* A speed indicator

`wget` does that really well. Your favorite language probably has one or two ready-to-use libraries for this.

If you can't achieve the full progress bar, as a lightweight alternative you can just display a counter: (`1/10`, `2/10`, etc.). If you do so, please make sure the user knows *what is being counted* !

# Remove noise

We already saw that people maybe running your tool without a terminal attached. In this case, you should skip displaying progress bars and the like.

Also, try to remove things that are only useful when debugging (or don't display them by default).

This includes the time taken to perform a given action (unless it's useful to the end-user, like if you are writing a test runner for instance). Also, don't forget that users can and will prefix their command line with `time` to get precise results if they need to.

A good technique to remove noise is to completely erase the last line before writing a new one.

Here's how to do it in Python:

```python
size = shutil.get_terminal_size()   # get the current size of the terminal
print(first_message, end="\r")
do_something()
print(" " * size.columns, end="\r")  # fill up the line with blanks
                                     # so that lines don't overlap
print(second_message)
```

Of course, this only works if the user does not need to know about the whole suite of messages!

# Tests

End-to-end tests are a great way to tweak the output without having to do a bunch of setup by hand, *and* check the error messages look good.


# Parting words

Well, that's all I've got today. Please keep those tips in mind when creating your own command line tool, and if you find a program that does not adhere to this rules, feel free to send patches. Until next time!


[^1]: Assuming they take the time to *read* the output. But the better they are, the more they're likely to get read :)
[^2]: If you are wondering, IDEs and services like Travis CI manage to display colors by creating a fake tty, running your tool as usual connected to it, and then re-interprenting ANSI codes. Using `isatty()` should still work in this case.
