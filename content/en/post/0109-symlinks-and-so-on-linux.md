---
authors: [dmerej]
slug: symlinks-and-so-files-on-linux
date: 2020-04-18T14:03:19.615132+00:00
draft: false
title: symlinks and .so files on linux - what you need to know
tags: [linux]
summary: |
  Everything you need to know about symlinks and .so files on Linux
---


# The issue

I've seen this happen countless times.

First, a Linux user asks for help about an error looking like this:

```
Error when running `bar`: `libfoo.so.5: no such file or directory`
```

Then, someone who's had the same issue suggests creating a symlink from `libfoo.so.6` to `libfoo.so.5`.

And then I come across the dialog some time later and I start crying.

Why do I cry - it looks like the problem is solved, right?

* the `bar` program seems to run just fine;
* the change was made with just one command (`sudo ln`) and can be undone easily (just remove the symlink);
* there was already a symlink from `libfoo.so` to `libfoo.so.6` anyway!

Well, despite the appearances, the problem is *not* solved, and doing this
is a *terrible idea* in general - like planting a ticking time bomb in the
street you live or shooting yourself in the foot because you've got a plantar wart.

But to understand why we need to talk about the language C, shared libraries,
soname bumps, Linux distributions, and package management.

And because I love telling stories, *you*, dear reader, will be the hero
in this one.

# Solving the Ultimate Question

Let's assume a group of people you don't really know (let's called them
*The Experts*), wrote a piece of C code than can get the answer to the
Ultimate Question of Life, the Universe, and Everything.

For obvious reasons, they want to keep the source code private, so here's
what they did:


* They wrote a *header file* containing the `get_answer` declaration named `answer.h` [^3]:

```c
// in answer.h
#pragma once
#ifdef __cplusplus
extern "C" {
#endif

char* get_answer();

#ifdef __cplusplus
}
#endif
```

* They created a *shared library* called `libanswer.so` from their source file (`answer.c`
  in this case):

```console
$ gcc -shared libanswer.so answer.c
```

That way, everyone who needs to get the answer to the Ultimate Question of Life, the
Universe, and Everything can buy the `libanswer.so` compiled library and the `answer.h` header
and call the `get_answer()` function - let's see how.

# Using the library from The Experts

You've bought the `libanswer.so` and `answer.h` files from The Experts
and have put them next to a file you've wrote named `print-answer.c`:

```c
// in print-answer.c
#include <stdio.h>
#include <answer.h>

int main() {
  char* answer = get_answer();
  printf("The answer is %s\n", answer);
  return 0;
}
```

You were told that `gcc` can compile C code and *link against* shared libraries
if you put them on the command line, so you try and run this:

```console
$ gcc libanswer.so print-answer.c -o print-answer
```

But it does not work, and you get the following error message:

```
print-answer.c:2:10: fatal error: answer.h: No such file or directory
```

Wait a minute - the `answer.h` file is *right there* - what does that mean,
"No such file or directory"?.

After a bit of research, you discover that `gcc` uses a list of paths called
the "include path" where it looks for headers. You check on your machine,
and sure enough, `/usr/include/` is one of the elements of this list, and `stdio.h`
is in `/usr/include/stdio.h`, which explains why `gcc` did not complain
about the first include.

To fix the compilation error, you add the `-I .` option to the command line
so that current directory is added to the list of include paths:

```console
$ gcc -I . libanswer.so print-answer.c -o print-answer
```

And then it compiles.

Now you try and run the `print-answer` program, but you get a new error message:

```console
$ ./print-answer
 error while loading shared libraries: libanswer.so
 cannot open shared object file: No such file or directory
```

It's the same error message as in the introduction and **the operating
system is lying to us**. The file `libanswer.so` is right there!  What's happening there?

After more investigation, you figure it out:  when you compiled the `print-answer`
executable, there was a small piece of binary inside it that recorded the *name*
of the `.so` file it was linked against. You can check it by running the `readelf` command and display
the *dynamic section* of your program:

```console
$ readelf -d ./print-answer
Dynamic section at offset 0x2de8 contains 27 entries:
  Tag        Type                         Name/Value
 0x0000000000000001 (NEEDED)             Shared library: [libanswer.so]
 0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
 ...
```

In a way, the `print-answer` program "knows" that it *needs* `libanswer.so`
to run. Crucially, it does not know nor cares about where `libanswer.so`
really *is*. [^5]

Then, when you run `./print-answer`, the operating system sees the name of the shared library in the
dynamic section and tries to locate it. Like `gcc`, it finds `libc.so.6` by itself (in
`/usr/lib/libc.so.6` for instance) - but it's unable to find the `libanswer.so` shared
library in the current directory.

Fortunately, you can fix that by using a special environment variable called `LD_LIBRARY_PATH`:

```console
$ LD_LIBRARY_PATH=. ./print-answer
The answer is 42
```

This time, the operating system looks for `libanswer.so` in the current directory, finds it, and
when required, invokes the code for the `get_answer()` function from the shared library.

That gets you thinking - you did not have to do any of this for `print-answer` to find the
`libc.so` library and the `stdio.h` header.

* What if it was possible to compile `libanswer.so` once and for all?
* And what if there was a way to compile the `print-answer.c` source file
without having to copy/paste the header and the shared library, and remember
all the various `gcc` options?


# Becoming a packager

Let's assume The Experts realized that their business model was not going
to work and decided to publish their source files for free instead. Yay
open source!

Here's the contents of their `answer.c` file:

```c
#include <answer.h>
#include <stdio.h>
#include <string.h>

char * get_answer() {
  // Disappointing, I know
  int r = 6 * 7;
  char buf[3];
  snprintf(buf, 3, "%d", r);
  return strdup(buf);
}
```

Since you are an Arch Linux user,  you decide to lookup documentation about the `pacman` package manager
and how generate and publish Arch Linux packages [^1].

After a while, you manage to write a working `PGKBUILD` for `libanswer`:

```bash
pkgname=libanswer
pkgver=1.0
pkgrel=1
pkgdesc="Answer the Ultimate Question"
arch=('x86_64')
...

build() {
  gcc -I . -shared answer.c -o libanswer.so
}

package ()
{
  mkdir -p $pkgdir/usr/{include,lib}
  install answer.h $pkgdir/usr/include/
  install libanswer.so $pkgdir/usr/lib
}
```

Then you build the package with `makepkg`

```bash
$ makepkg
==> Making package: libanswer 1.0-1
...
==> Finished making: libanswer 1.0-1
```

Everything goes well, and you now have a file named `libanswer-1.0-1-x86_64.pkg.tar.xz`
next to your `PGKBUILD`.

You install the package with `pacman`:

```console
$ sudo pacman -U libanswer-1.0-1-x86_64.pkg.tar.xz
```

Then you find out that you can compile and run `print-answer.c` from anywhere
in the system using the following commands:

```bash
$ gcc print-answer.c -lanswer -o ./print-answer
$ ./print-answer
The answer is 42
```

This time you need only the *name* of the library (the part without the
`lib` prefix and the `.so` suffix) after the `-l` option. You do *not*
have to worry about include paths or use the `LD_LIBRARY_PATH` environment
variable -  neat!

What you've accomplished is called *packaging the `answer` library*, and it's
what  *package maintainers* do - well done.

Impressed by your packaging skills[^2], the Arch Linux maintainers allow
you to publish your package in official repositories, which means
everyone using Arch Linux is now able to install the `libanswer` package in
just one command!

# A simple change

A few days later, The Experts release a new version of their library (1.1), containing a nice optimization:

```c
char* get_answer() {
  return strdup("42");
}
```

Since you are the maintainer of the `libanswer` package, you quickly update
the PKGBUILD and publish a new release.


```diff
-pkgver=1.0
+pkgver=1.1
 pkgrel=1
 pkgdesc="Answers the Ultimate Question"
 arch=('x86_64')
 source=(...)
```

You build and install the package on your machine and check it still works:

```console
$ makepg
$ sudo pacman -U libanswer-1.1-1-x86_64.pkg.tar.xz
```

And then you publish the new version of the `libanswer` package.

That's where Linux distributions really shine (and the whole reason we use
shared libraries in the first place).  Once the new package is published,
*any* Arch Linux user who installs it will get the latest version
of `libanswer.so` in their system, and all the programs that were linked
against it will use the latest version - this is especially important if the
new version contains a security bug fix for instance.


# Another change

A week later, The Experts realize they don't really need to return a string
from the ` get_answer()`  function, and that a simple `int` would suffice.

So they modify both their header and source files:

```diff
- char* get_answer();
+ int get_answer();
```

```c
#include <answer.h>

int get_answer() {
  return 42;
}
```

And they publish a release note:

```md
# The answer project

## Version 2.0

* Change the return type of the `get_answer()` function from `char*` to `int`.

## Version 1.1

* This release implements performance optimizations.

## Version 1.0

* First public release!
```

Upon hearing the good news, you download the latest sources of the project,
and you modify your `print-answer.c` source file to use the latest version
of the library:

```c
#include <stdio.h>
#include <answer.h>

int main() {
  int answer = get_answer();
  printf("The answer is %d\n", answer);
}

```

You compile everything and check the code still works:

```
$ gcc -I . -shared answer.c -o libanswer.so
$ gcc -I . libanswer.so print-answer.c -o ./print-answer
$ LD_LIBRARY_PATH=. ./print-answer
The answer is 42
```

Time to publish the v2!

```diff
-pkgver=1.0
+pkgver=2.0
 pkgrel=1
 pkgdesc="Answers the Ultimate Question"
 arch=('x86_64')
 source=(...)
```

```console
$ makepg
$ sudo pacman -U libanswer-2.0-1-x86_64.pkg.tar.xz
```

Easy as pie - satisfied, you publish the new package and go to bed.


# When shit hits the fan

The next morning you receive the following e-mail:

```
Subject : latest libanswer package update broke display-answer-pp program

Hello,

I'm using `display-answer-pp` version 0.4, and when I updated `libanswer` to
the version 2.0, I got the following error:

./display-answer-pp
zsh: segmentation fault (core dumped)  ./display-answer-pp

Downgrading the `libanswer` package fixes the problem. Please advise.

Signed: Bob
```

Welcome to the joys of packaging!

You've never heard of the `display-answer-pp` package - what is going on?

After a bit of research, you find out that someone wrote a `display-answer-pp`
program using your `libanswer` package and published it on the official Arch Linux
repositories a few days ago.

Here's what the code for `display-answer-pp` looks like - it's a single `C++` file:

```cpp
#include <answer.h>
#include <iostream>

int main() {
    auto answer = get_answer();
    std::cout << "The answer is: " << answer << std::endl;
    return 0;
}
```

So what happened?

Well, the problem is that you forgot to coordinate with your fellow packagers!

You see, when `display-answer-pp` was being packaged, the `get_answer()`
function was returning a `char*`. When you published `answer` version 2.0,
the code for the function `get_answer()` started returning an
`int` instead.

So when Bob updated `libanswer` after having installed `display-answer-pp`,
and tried to re-run the program, all hell break loose, because the compiled
C++ code expected a *pointer* to a string and got an *int* instead.

In other terms, the *application _binary_ interface* (or ABI for short) of the `libanswer` library broke.

# You break it, you fix it

Unfortunately, there's only one way to fix an ABI breakage: you need to
*recompile* everything that was linked against the old version of the library.

That's one of the main issues package maintainers have to solve. They need two very different features when it comes
to libraries updates:

* If the new version of the library is ABI-compatible with the previous one, end-users should be able to get it
  by simply updating *the one package* that contains it.

* If not, they need to make sure *none of the programs that depend on the library* break when the update is made.

## The Arch Way

Here's how Arch maintainers solve this problem. In our example, they would have published `libanswer` v2
in a special repository named "staging". Then, they would have rebuild every package that depends
on `libanswer` (so both `print-answer` and `display-answer-pp`) and pushed those to the staging repository.

Finally, after a period of testing, they would have moved `libanswer`, `print-answer` and `display-answer-pp`
in the official repositories in one swift update. They would have used a *to do list* like
[this one](https://www.archlinux.org/todo/hdf5-1120-release/) to coordinate the packaging tasks.

This means that if you try and update `libanswer` without upgrading *every
other package* that depends on it, you risk breaking your installation -
and that's why partial updates are not supported on Arch Linux.

## The Debian Way

Debian maintainers use another strategy. When they package a library,
they include its version number in the name of the package. What's more,
they have a separate *development* package that contains the files required for
compiling programs that use the library. They also use a compilation trick
called the `soname` option.

Let's see how this works.

First, they tell `gcc` to use the correct soname option when linking the library [^7]:

```console
$ gcc -I . answer.c -shared -Wl,-soname=libanswer.so.1 -o libanswer.so.1
```

They use the outcome of the build to generate two packages:

* `libanswer-dev`, that contains a symlink `libanswer.so -> libanswer.so.1` and the `answer.h` header
* and `libanswer1`, that contains **only** the `libanswer.so.1` file

Then, they build `display-answer-pp` for the first time, using the `libanswer-dev` package:

```console
$ g++ -lanswer display-answer.cpp -o ./display-answer-pp
```

Because `libanswer.so` was built with the `-soname=libanswer.so.1` option, the `display-answer-pp` binary
now *knows* that it needs `libanswer.so.1` at runtime:

```console
$ readelf -d display-answer-pp
Tag                  Type               Name/value
0x0000000000000001 (NEEDED)             Shared library: [libanswer.so.1]
...
```

When the v2 version of `libanswer` is published by The Experts, they rebuild
the shared library with an appropriate soname:

```console
$ gcc -I . answer.c -shared -Wl,-soname=libanswer.so.2 -o libanswer.so.2
```

They use the outcome of the build to *update* the `libanswer-dev` package and to create
a *brand new* `libanswer2` package.

At this point:
* `libanswer-dev` contains a symlink `libanswer.so -> libanswer.so.2` and the updated `answer.h` header
* `libanswer2` contains only the `libanswer.so.2` file

Then, they build `display-answer-pp` for the second time, using the updated `libanswer-dev` package:

```console
$ g++ -lanswer display-answer.cpp -o ./display-answer
```

This time, `display-answer-pp` knows that it needs `libanswer.so.2` at runtime:

```console
$ readelf -d display-answer-pp
Tag                  Type               Name/value
0x0000000000000001 (NEEDED)             Shared library: [libanswer.so.2]
...
```

Let's sum up:

* Both `libanswer1` and `libanswer2` packages can co-exist in the same system,
  since they contain different filenames
* The `libanswer-dev` package does not need to be installed for
  `display-answer-pp` to run since the program contain the versioned soname
  in its dynamic section
* If you want to rebuild a program when a new version of the library is out,
  you just install the latest `libanswer-dev` package - the command used for
  compilation does not have to change at all!

Clever, right?

Because of this technique, the update from `libanswer` v1 to `libanswer`
v2 is often called *a soname bump* - the update from `v1` to `v1.1` is just
a regular update.

Quite often, a backward incompatible update correspond to the first digit
of the soname to be updated. [^8]

# Conclusion

Now you know - different versions of a library have various sonames, and
the symlinks are carefully crafted by distribution maintainers.

So, when you create a symlink yourself, you are taking a huge risk, especially
when creating links between libraries that have a different leading digit in
their soname!

As we saw, using the incorrect library at runtime can cause crashes, and if
you break an essential binary (like `bash` for instance), you may no longer
be able to log in, which means your only choice may be to re-install your whole system
from scratch. This is not theoretical by the way: it happened to me *years ago*,
and I still remember it to this day.

So, what to do if you get this error?

```
Error when running `bar`: `libfoo.so.5: no such file or directory`
```

* If `bar` comes from a package on your distribution, update all packages
  and then open a bug report if the problem persists
* If not, try and re-compile `bar` - possibly after updating the `libfoo-dev` package.

But *please*, *please* do not create a symlink from `libfoo.so.6` to
`libfoo.so.5` or suggest this solution to someone else.  Together, let's
put an end to this bad, bad, advice. Thank you!


[^1]: You're using Arch Linux because you're cool and you want to learn - good for you!
[^2]: Reminder: it's a story I made up!
[^3]: If you're puzzled by the `__cplusplus` stuff don't worry - it's just so that the answer library
      is usable from C++ too.
[^5]: By the way, it needs `libc.so` because the compiled code for `printf` lives there.
[^7]: Actually, this is often done automatically by whatever build system the library is using
[^8]: Sadly it's not always the case: `lua` and `libpng` are notable exceptions.
