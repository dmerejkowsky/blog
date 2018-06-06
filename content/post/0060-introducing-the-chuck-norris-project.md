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

1. [Using CMake and Ninja]({{< ref "post/0061-let-s-build-chuck-norris-part-1-cmake-and-ninja.md" >}})
2. [Managing third-party dependencies with conan]({{< ref "post/0062-let-s-build-chuck-norris-part-2-sqlite-and-conan.md" >}})
3. [Exposing a C API on top of C++ code]({{< ref "post/0063-let-s-build-chuck-norris-part-3-a-c-wrapper.md" >}})
4. [Using Python with ctypes]({{< ref "post/0064-let-s-build-chuck-norris-part-4-python-and-ctypes.md" >}})
5. [Using cffi to build a Python extension]({{< ref "post/0065-let-s-build-chuck-norris-part-5-python-and-cffi.md" >}})
6. [Cross-compiling for Android]({{< ref "post/0073-let-s-build-chuck-norris-part-6-android-cross-compilation.md" >}})

Planned for later:

* Using C++ in an iOS application
