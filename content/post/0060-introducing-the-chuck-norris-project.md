---
slug: introducing-the-chuck-norris-project
date: 2018-03-10T12:35:38.025713+00:00
draft: false
title: Introducing the "Let's Build Chuck Norris!" Project
tags: [c++]
authors: [dmerej]
---

# The ChuckNorris library

The Chuck Norris library is written in C++ and contains a class able to give you random Chuck Norris facts when the `getFact()` method is called:

Here's how to use it:

```c++
#include <ChuckNorris.hpp>

ChuckNorris chuckNorris;
std::string fact = chuckNorris.getFact();
```

{{< note >}}
You will find all the source code on [GitHub](https://github.com/dmerejkowsky/chucknorris).
{{< /note >}}


# Let's build Chuck Norris!

"Let's Build Chuck Norris!" is a on-going series of blog posts aiming at exploring various topics about C++ and build systems:

Available:

* [Using CMake and Ninja]({{< ref "post/0061-let-s-build-chuck-norris-part-1-cmake-and-ninja.md" >}})
* [Managing third-party dependencies with conan]({{< ref "post/0062-let-s-build-chuck-norris-part-2-sqlite-and-conan.md" >}})
* [Exposing a C API on top of C++ code]({{< ref "post/0063-let-s-build-chuck-norris-part-3-a-c-wrapper.md" >}})

Planned for later:

* Using cffi to build a Python extension
* Using C++ in an Android application
* Using C++ in an iOS application
