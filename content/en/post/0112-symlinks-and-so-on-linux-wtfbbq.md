---
authors: [dmerej]
slug: symlinks-and-so-on-linux-omg-wtf-bbq
date: 2020-04-18T14:03:19.615132+00:00
draft: true
title: "symlinks and .so on linux - OMG-WTF-BBQ ?@#+!"
tags: [linux]
summary: |
  Everything you need to know about symlinks and
  .so files on Linux - except if you don't mind
  breaking your installation beyond all repair.
---


# The issue

I've seen this happen countless times.

* First, a Linux user asks for help about an error looking like this:

```
Error when running `bar`: `libfoo.so.5: no such file or directory`
```

* Then, someone who's had the same issue suggests creating a symlink from `libfoo.so.6` to
`libfoo.so.5`.

* And then I come across the dialog some time later and I start crying.

Why do I cry - because  both users think they've solve their problem ; and indeed:

* `bar` seems to work just fine;
* the change was made with just one command `sudo ln` command and can be undone
  easily (just remove the symlink);
* there was already a symlink from `libfoo` to `libfoo.so.6` anyway!

But in general, doing this is a *terrible idea*, like shooting yourself in
the foot because you've got plantar wart.

But too understand why, we need to talk about the language C, shared libraries,
soname bumps, Linux distributions and package management.

# Solving the Ultimate Question

Let's assume a group of people you don't know really  (let's called them
*The Experts*), wrote a piece of some C code in a file called `answer.c`
than can get the answer to the Ultimate Question of Life, the Universe
and Everything.

For obvious reasons, they wanted to keep the source code (aka the `.c` file) private,
so here's what they did:


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

* They created a *shared library* called `libanswer.so` from their source file:

```console
$ gcc -shared libanswer.so answer.c
```

That way, everyone who needs to get the answer to the Ultimate Question of Life, the
Universe and Everything, from their code can just call the `get_answer` function
they've implemented -  and they *only* needs the two files.

# Using code from The Experts

Now let's say you were asked by a big customer to write a program that will
print the answer to the Ultimate Question of Life, Universe and Everything
on the command line.

You've managed  to get your hands on the `libanswer.so` and `answer.h`
and have put them next to your `print-answer.c` source file:

```c
// in print-answer.c
#include <stdio.h>
#include <answer.h>

int main() {
  char* answer = get_answer();
  printf("The answer is  %s", answer);
  return 0
}
```

You were told that `gcc` can compile C code and *link with* shared libraries
if you put them on the command line, so your try and run this:

```console
$ gcc libanswer.so print-answer.c -o print-answer
```

But this does not work, you get:

```
print-answer.c:2:10: fatal error: answer.h: No such file or directory
```

Wait a minute - the `answer.h` file is *right there* - what do that mean,
"No such file or directory"?.

Upon reading stuff on the Internet, you discover is that `gcc` has a list named
the "include path" where it looks for headers. You check oun your machine,
and sure enough, `/usr/include/` is on an element of this list, and `stdio.h`
is in `/usr/include/stdio.h`, which explains why `gcc` did not complain
about the first include.

So, to fix the compilation error, you add the `-I .` option to the command line
so that current directory is added to the list of include paths:

```console
$ gcc -I . libanswer.so print-answer.c -o print-answer
```

And then it compiles.

Now you try to run the `print-answer` program, and you get:

```console
$ ./print-answer
 error while loading shared libraries: libanswer.so
 cannot open shared object file: No such file or directory
```

It's the same error message as in the introduction, and **the operating
system is lying to us**. The file `libfoo.so` is right there!  What's happening there?

After more investigation, you figure it out :  when you compiled the `bar`
executable, there was a small piece of binary inside that recorded the *name*
of the `.so` file we used. You check it by running the `readelf` command:

```console
$ readelf -d ./bar
Dynamic section at offset 0x2de8 contains 27 entries:
  Tag        Type                         Name/Value
 0x0000000000000001 (NEEDED)             Shared library: [libanswer.so]
 0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
# Distributing shared libraries
```

It's in the `dynamic` section because after this point, `bar` only knows that it *needs* `libfoo.so`,
to run, but it does not know where `libanswer.so`. By the way, it needs `libc.so` because the compiled
code for `printf` lives there.

Then, when you ran `./bar`, the operating systems sees the name of the shared library in the
dynamic section and tries to locate them. Like `gcc`, it found `libc.so.6` by itself (in
`/usr/lib/libc.so.6` on my machine) - but was unable to find it in the current directory.

You decide to fix that by using the `LD_LIBRARY_PATH` environment variable:

```console
$ LD_LIBRARY_PATH=. ./bar
The answer is 42
```

# Looking for an other way

Let's assume The Experts realized that their business model was not going
to work and decided to publish the `answer.c` file to the world.

Here's its contents:

```c
// in answer.c
# include <answer.h>
char * get_answer() {
    return "42";
}
```

(Disappointing, I know).

And that gets you thinking:

* What if it was possible to compile `libanswer.so` once and for all?
* And what if if there was a way to compile our `print-answer.c` source file
without to copy/paste the headers and shared library files, and remembering
all the various `gcc` options?

After reading the Arch Linux wiki [^1], you decide to use a *package manager* - (`pacman` in this case).

First, you write a `PGKBUILD` for libanswer:

```bash
pkgname=libanswer
pkgver=1.0
pkgrel=1
pkgdesc="Answers the Ultimate Question"
arch=('x86_64')
source=(answer.c answer.h)
md5sums=('e99414287d9f62931a2c67cdfa1b9ca7'
         'e4b4ca61630856dcd054f604f42f73ca')

build() {
  gcc -I . -shared answer.c -o libanswer.so
}

package ()
{
  mkdir -p $pkgdir/usr/{include,lib}
  install -p answer.h $pkgdir/usr/include/
  install -p libanswer.so $pkgdir/usr/lib
}
```

Then you build the package:

```bash
$ makepkg
==> Making package: answer 1.0-1
... # bunch of stuff there
==> Finished making: answer 1.0-1
```

I won't explain everything that went on there, but suffice to know there is now a
file named `libanswer-1.0-1-x86_64.pkg.tar.xz`  (aka a *package*) next to our
`PGKBUILD`.

You install the packgae with `pacman`:

```console
$ sudo pacman -U libanswer-1.0-1-x86_64.pkg.tar.xz
```

And then you notice you can compile and run `print-answer.c` from anywhere in the system:

```
$ gcc print-answer.c -lanswer -o ./print-answer
$ ./print-answer
The answer is 42
```

You still needs to tell `gcc` that the `print-answer` binary depends
on the `answer` library, this time you need only its *name* (the part without
the `lib` prefix and the `.so` suffix) after the `-l` option.

Neat!

You've just *packaged* the `answer` library for Arch Linux, and it's what *packagers* or
*distributions maintainers* do.

Impressed by your packaging skills[^2], the Arch developers allow you to publish your
package in the Arch Linux official repositories.

An now, everyone using Arch Linux will be able to install the `libanswer` package in just a few commands!


# An important change

Alas, the only thing that never change in the software world is that everything sometimes changes.

This time, the experts realized they don't need a whole string for the answer function, and that
a simple `int` would suffice.

So they changed both their `answer.c` and `answer.h`:

```c
#include <answer.h>

int get_answer;
```

```c
#include <answer.c>

int get_answer() {
  return 42;
}
```

and they published a release note:

```md
# The answer project

## Version 2.0

Version 2.0 changed the return of the `get_answer()` function from `char*` to
`int`.

## Version 1.0

First public release!
```

Upon hearing the news, you download the latest sources of the projects, and you adapt the
`print-answer.c` file to have:

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
 source=(answer.c answer.h)
-md5sums=('e99414287d9f62931a2c67cdfa1b9ca7'
-         'e4b4ca61630856dcd054f604f42f73ca')
+md5sums=('74ed7abc67abd5638b71fd4d662be997'
+         '1282d8abb12b68b772bae0387fb0a664')
```

You first build and install the version 2 of the `libanswer` package:

```console
$ makepg
$ sudo pacman -U libanswer-2.0-1-x86_64.pkg.tar.xz
```

Confident in your newly packaging skills you push the version 2.0 of the package
to the Arch Linux repository and go to bed.


# When shit hits the fan

The following morning you receive the following e-mail:


```
Subject : latest libanswer  package update brokedisplay-answer

Hello,

I'm using `display-answer` version 0.4, and when I upgraded `libanswer` to
the version 2.0, I got the following error:

./display-answer
zsh: segmentation fault (core dumped)  ./display-answer-pp

Downgrading the `libanswer` package fixes the problem. Please advise.

Signed: Bob
```

Welcome to the joy of packaging!

You've never heard of the `display-answer-pp` package - what is going on?

After a bit of research, you find out that someone wrote a `display-answer-pp` program, this
time in C++, and decided to publish it on Arch Linux repositories too.

Here's what the code for `display-answer-pp` looks like - it's a single `main.cpp` file:

```cpp
#include <answer.h>
#include <iostream>

int main() {
    auto answer = get_answer();
    std::cout << "The answer is: '" << answer << "'" << std::endl;
    return 0;
}
```

So what happened?

Well, the problem is that you forgot to coordinate with your fellow packagers!

You see, sometime between the 1.0 release and the 2.0 publication of the `libanswer` version 2.0
package, an other packager wrote a `PKGBUILD` for `display-answer-pp` and published it.

Back then, `get_answer()` answer was returning an `char *`.

But when you published `answer` version 2.0, the code for the function `get_answer()` started returning an
`int` instead.

So when Bob upgraded `libanswer` after having installed `display-answer-pp`, and tried to re-run the program,
all hell break loose, because the compiled C++ code expected a *pointer* to a string and got an *int* instead.

In other terms, you broke the *application _binary_ interface* (or ABI for short).

# You break it, you fix it

Unfortunately, there's only one way to fix an ABI breakage : you need to *recompile* everything that
was linked against the old version of the library. (Interestingly, in our contrived C++ example, the
source code of the programs sometimes do not even have to change!)

Every Linux distribution faces this problem, and they use different strategies for that.

[^1]: You're using Arch Linux because you're cool and you want to learn - good for you!
[^2]: Reminder: it's a story I made up!
[^3]: If you've puzzled by the `__cplusplus` stuff don't worry - it's just so that the answer library
      is usable from C++ too.
