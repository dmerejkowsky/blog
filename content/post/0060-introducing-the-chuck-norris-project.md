---
slug: introducing-the-chuck-norris-project
date: 2018-03-10T12:35:38.025713+00:00
draft: false
title: Introducing the "Let's Build Chuck Norris!" Project
tags: [c++]
authors: [dmerej]
---

# The Chuck Norris Project

The Chuck Norris Project a C++ library that contains a class able to give you random Chuck Norris facts when the `getFact()` method is called:

Here's how to use it:

```c++
#include <chucknorris.hpp>

ChuckNorris chuckNorris;
std::string fact = chuckNorris.getFact();
```

{{< note >}}
You will find all the source code on [GitHub](https://github.com/dmerejkowsky/chucknorris).
{{< /note >}}


The "Let's Build Chuck Norris!" project is a series of blog posts aiming at exploring various topics about C++ and build systems:


* Using CMake and Ninja
* Managing third-party dependencies
* Exposing a C API on top of C++ code
* Using cffi to build a Python extension
* Using C++ in an Android application
* Using C++ in an iOS application


Interested? Let's start with part one: [CMake and Ninja]({{< ref "0061-let-s-build-chuck-norris-part-1-cmake-and-ninja.md" >}}).
