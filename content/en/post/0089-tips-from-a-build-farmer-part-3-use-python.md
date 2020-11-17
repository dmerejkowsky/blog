---
authors: [dmerej]
slug: tips-from-a-build-farmer-part-2-some-concepts
date: "2018-10-18T18:17:04.151310+00:00"
draft: true
title: "Tips From a Build Farmer - Part 3: Use Python"
tags: [ci]
summary: Why you should consider writing your CI scripts in Python
---

[Last time]({{< ref "/post/0084-tips-from-a-build-farmer-part-2-some-concepts.md" >}}) we asked ourselves: "What language should I use to write CI scripts?".

Based on my experience, (I've been writing and maintaining CI scripts for almost 10 years): there's only one good answer: Python.

I've seen CI scripts written in Bash, Powershell or even Batch, I've re-written many of them in Python, and it has *always* paid off big time.

Does this mean *you* should rewrite your own scripts too? Definitely not! Don't base your decisions based solely on the experience of *one individual*. Just keep reading and hopefully the arguments and example I'll be given here will help you to take the correct decision.

But let's start at the beginning.

# The naive approach

Let's say you are building a Rust project. You want to make sure it builds correctly.

Also let's assume you are using GitLab CI. [^1]

Here's what you might write in you `.gitlab-ci.yml`

```yaml

stages:
  - ci

build_and_test:
  stage: ci
  script:
    - cargo build --release
    - cargo test --release
```

This works quite well.

My advice though is to replace the script lines by a call to a bash script:

```yaml
# ...
build_and_test:
  stage: ci
  script:
    - ./ci.sh
```

```bash
#!/bin/bash
set -x
set -e
cargo build --release
cargo test --release
```

Why? Simply because it allows developers (and you, dear maintainer), to edit and run the `ci.sh` directly.

# How to use Python

So now you've put your CI code in a separate file, away from the *configuration*, let  me suggest you write your code in Python, and
only keep the code required to install and run python in your `.gitlab-ci.yml` file:

```yaml
windows:
  - choco install python
  - /c/python37/python ci/ci.py

mac:
  - brew install python
  - /usr/local/bin/python3 ci/ci.py

linux:
  - python3 ci/ci.py
```

And then write all your CI code in a cross-platform `ci.py` script


# Why Python

I'm truly convinced Python is better suited for thask. It's readable, maintainable, and easy to learn.

The fact you have to install it separately on macOS is not an excuse, and actually a good thing: the built-in python that comes with macOS is outdated (it's Python2, not Python3), close source, and you may break things if you use it.

So let's take a look at how Python features help you [fight the fear]({{< ref "/post/0083-tips-from-a-build-farmer-part-1-ci-scripts-are-scary.md" >}}) associated with writing and maintaining CI scripts.

[^1]: I'm assuming that because it's what we use at work, but the advice I'll be giving here will apply also for travis or even Jenkins.

# Strong cross-platform support

Python is commonly used for cross-platform support. It's Windows support in particular is outstanding compared to other "scripting languages". It's probably because many people work with Python on Windows, and that many Python maintainers also run Windows.

# Easy to learn

Learning Python is quite easy. You can grok its simple features quite rapidly, even if its syntax is sometimes somewhat unique.

If your team mates already know an other programming language, you can get them up to speed by teaching them about:

* The mutable default argument weirdness (Why `def foo(a, b=list())` probably does not do why you expect
* The syntax for default and keyword-only arguments: `def foo(a, b, c=False),  `def foo(a, b, *, c)`, and so on.
* The fact that everything is passed by reference
* The list comprehensions
