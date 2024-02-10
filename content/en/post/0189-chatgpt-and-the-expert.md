---
authors: [dmerej]
slug: chatgpt-and-the-expert
date: 2024-02-10T15:35:24.407325+00:00
draft: true
title: "ChatGPT And The Expert"
tags: [misc]
summary: |
  Should you be using ChatGPT to answer technical questions?
---


# A brief history of Python

Let's talk about Python 2.8  for a second ;)

Python 2.8 does not really exist, officially we went from Python 2.7 to Python 3.0

See PEP 404: https://peps.python.org/pep-0404/

There was a python fork  called Tauthon
https://github.com/naftaliharris/tauthon ... and even a fork of tauthon called Python2.8:
https://github.com/exarkun/python2.8

The whole point of python 2.8 is that you could get the new changes from the 3.0 version, without backward-incompatible changes

I think both projects are mostly dead now

# The expert

Yes, I'm the expert :)

* 15 years of writting Python code
* I've actually ported a non-trivial project from Python 2 to 3 and [blogged about it]() - in French - and [in English]()

# The trick quetsion

> How do I migrate from Python 2.7 to Python 2.8 ?

# ChatGPT's answer

Migrating from Python 2.7 to Python 3 is a crucial step, especially since Python 2 reached its official end-of-life at the start of 2020. Here's a guide to help you transition your code:

Assess Your Codebase:
 
  * Focus on supporting Python 2.7 initially.
  * Ensure you have good test coverage (you can use coverage.py for this).
  * Familiarize yourself with the differences between Python 2 and 3.

Use Futurize or Modernize:
 
  * Install the future package using `python -m pip install future`.
  * Use Futurize (or Modernize) to update your code. For example:

```console
$ python -m pip install future
$ python -m pip install pylint
$ python -m pip install caniusepython3
$ python -m pip install tox
$ python -m pip install mypy
```

These tools will help you make your code compatible with both Python 2 and 3.

* Specify Python Versions in setup.py:  In your setup.py file, specify
  the proper trove classifier to indicate which versions of Python you
  support. Since your project doesn't yet support Python 3, include:

```
Programming Language :: Python :: 2 :: Only
```

Remember that even if you're forced to support Python 2 due to
dependencies, embracing Python 3 practices can lead to cleaner code.
Ideally, focus on Python 2.7 compatibility, as it was the last supported
version of Python 2. If possible, skip Python 2.5 and older versions to
minimize changes in your codebase. 🐍🔀

For more detailed information, refer to the official Python 3 documentation (1).

Source: Conversation with Bing, 2/9/2024

Notes:

1. How to port Python 2 Code to Python 3. https://docs.python.org/3/howto/pyporting.html.
2. How to update system python 2.7 to 3.x in Ubuntu 20.x after upgrade. https://askubuntu.com/questions/1277240/how-to-update-system-python-2-7-to-3-x-in-ubuntu-20-x-after-upgrade.
3. Python 2.7 to 3.X Migration Guide: How to Port from Python 2 ... - STX Next. https://www.stxnext.com/blog/python-3-migration-guide/.
4. Upgrading Python 2.7 to 3.8 : Recommended? - Ask Different. https://apple.stackexchange.com/questions/409331/upgrading-python-2-7-to-3-8-recommended.
5. Convert python 2.7 to python 3.8 - Stack Overflow. https://stackoverflow.com/questions/61097855/convert-python-2-7-to-python-3-8.
6. undefined. https://pythonconverter.com/.

## Some notes about ChatGPT answer

Some notes
 - tox for running the same test suite with several python Versions is a good Ideally
 - mypy is probably not useful, unless you had type annotations 10 years ago (which is unlikely)
 - future to do the upgrade (assuming you want to keep compatibility with 2!)
 - caniusepython3 is completly useless now that all major lib support python3 (but it was _very_ useful during the transition)
 - `Programming Language :: Python :: 2 :: Only` is the opposite of what you want!
 - "If possible, skip 2.5" - here ChatGPT is confused because indeed, switching from 2.7 to 3.6 was much easier than switching t
    earlier Python versions 
- I kind a love the `undefined`  before the link to pythonconverter.com (which was probably just a random online converter, but is now dead)

What's even more interesting is that there's no way to know (if you're not already familiar with Python history) that something is missing !

(namely, the stuff about Python 2.8 I talked about in the above post)

## Parting words

By the way, I'm boycotting Generative IA in general and ChatGPT in particular, so
this is hopefully the last time I _have_ to use it - I just needed a good example
to talk about ChatGPT with fellow programmers and I think I finally found one.
