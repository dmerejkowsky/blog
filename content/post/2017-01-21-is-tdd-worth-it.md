---
slug: is-tdd-worth-it
date: 2017-01-21T12:52:53.361088+00:00
draft: false
title: Is TDD Worth It?
---

Well, here is a good question!
Here's what I have to say:

1. I don't know
2. It depends

Those are, by the way, two very valid answers you can give
to any question. It's OK to not have a universal answer to
everything ;)

Still, I guess you want me to elaborate a tad more, so here goes ...

<!--more-->

## My testing story

I'll start by describing my own experience with testing in general, and TDD more
specifically. Hopefully it will help you understand how I came to the above
answer. It's a long story, so if you prefer, you can jump directly to the
conclusion.

### Shipping software

The story begins during my first "real" job.
I was working in a team that had already written quite a few lines of
`C++` code. We were using `CMake` and had several `git` repositories.

So I wrote a command-line tool in Python named `toc`[1] that would:

* Allow developers to fetch all the git repositories into a common "workspace"
* Run `CMake` with the correct options to configure and build all the
  projects.

The idea was to abstract away the nasty details of cross-platform `C++`
compilation, so that developers could concentrate on how implement the
algorithms and features they were thinking about, without having to care
on such low-level details such as the build system.

The tool quickly became widely used by members of my team, because the
command line API was nice and easy to remember.

```console
$ cd workspace
$ toc configure
$ toc build
```

It also became to be used on the buildfarm, both for continuous integration
and release scripts.

So I had to add new features to the tools, but without breaking the workflow of
my fellow developers.

Testing by hand was tedious, so I started writing tests.

### Dark days: bad tests

The first test I wrote were not very good.

Basically, I had a bunch of "example" code, like this:

```text

test
  world
    CMakeLists.txt
    world.h
    world.cpp
  hello
    CMakeLists.txt
    main.cpp
```

The `world` project contained source code for a shared library,
(`libworld.so`), and the `hello` project contained source code for an
executable (`hello-bin`) that was using `libworld.so`.

The tests looked like:

```python
class


[^1]: "Toc means Obvious Compilation". Yes, it was a silly name.
