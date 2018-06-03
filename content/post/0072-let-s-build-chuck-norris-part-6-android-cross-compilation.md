---
authors: [dmerej]
slug: chuck-norris-part-6-android-cross-compilation
date: 2018-06-02T10:17:17.789657+00:00
draft: false
title: "Let's Build Chuck Norris! - Part 6: Cross-compilation for Android"
tags: [c++]
---

_Note: This is part 6 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._


# Introduction

Cross-compilation is a tricky subject.

In order to keep things simple, in this article we'll only try and run a simple "Hello,world" program written in C inside a simulator and on our phone.

Let's get started!

# A naive try

Let's see what happens if we naively try to run some C code on our phone.

First, let's install the Android SDK so that we can use the `adb` tool.

Then, let's activate the developer mode on the phone, and plug it to our laptop.

Now let's compile a simple C program:

```c
/* in hello.c */
#include <stdio.h>

int main() {
  printf("Hello, world\n");
  retrun 0;
}
```

```bash
$ gcc hello.c -o hello
```

And now, let's use `adb push` to copy the binary on our phone, and `adb shell` to try and run it:

(Note that `/data/local/tmp` is the only folder I found where we can run executables):


```bash
$ adb push hello /data/local/tmp
$ adb shell
$ cd /data/local/tmp
$ ./hello
/system/bin/sh: ./hello: not executable: 64-bit ELF file
```

Hum. What just happened ?

# CPU architectures

When you compile some code, you get a binary file from the source code. You can think of this binary file as a list of instructions, ready to be used by a CPU.

The trick is that different CPU have different *instructions sets*.

For instance, it is very likely that the CPU you have on your laptop in a `x86_64` CPU, and that the CPU of you phone is an `arm`.

This means that a binary you built for a `x86_64` CPU on your laptop will not run on the `armv7` CPU of your phone.


# The libc

OK, but the Android also comes with a simulator, and we can choose the CPU architecture.

Can't we just use a `x86_64` Android simulator ?

If we try the same thing with a `x86_64` simulator, we will get an even weirder error:

```bash
$ adb push hello /data/local/tmp
$ adb shell
$ cd /data/local/tmp
$ ./hello
/system/bin/sh: ./hello: no such file or directory
```

The file does exist, but Android does not know how to run it. Why?


Remember when we used `LD_TRACE_LOADED_OBJECTS` back in [a previous post](
{{< ref "post/0064-let-s-build-chuck-norris-part-4-python-and-ctypes.md#using-the-chucknorris-shared-library" >}})?

Well, if we re-run the binary we just built we can see it loads a few `.so` files:

```bash
$ export LD_TRACE_LOADED_OBJECTS=1
$ ./hello

	linux-vdso.so.1 (0x00007ffc1ad96000)
	libc.so.6 => /usr/lib/libc.so.6 (0x00007fb017147000)
	/lib64/ld-linux-x86-64.so.2 (0x00007fb017503000)
```

Those files do not exist on Android, because even if Android is based on Linux, it's still a different operating system.

See the line about `libc.so.6` ? That's the library that contains the code for the `printf` function we just used.

We call such a library "the libc", which is a bit misleading.

There are several *implementations* of "the libc". On your laptop you are probably using `glibc`. There are other implementations like `musl` for instance. Android uses yet an other implementation called `bionic`.

So if want to achieve our goal (running the "Hello, world" C program on a simulator and on a phone), we have to do two things:

1. Make sure we can tell the compiler about the CPU architecture
2. Make sure we use the correct libc

This is tricky because by default, compilers use the  same CPU architecture and the same libc used by the operating system they run on[^1].

And this is what we call "cross-compilation".

# Using the NDK to compile by hand

Google provides a set of tools know as the *NDK* in order to help us cross-compiling code for Android.

If we download and extract the NDK, here's how we can compile and link our "Hello, World" program:

```bash
export NDK_ROOT=/path/to/ndk

${NDK_ROOT}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang \
  --target=x86_64-none-linux-android \
  --gcc-toolchain=${NDK_ROOT}/toolchains/x86_64-4.9/prebuilt/linux-x86_64 \
  --sysroot=${NDK_ROOT}/sysroot \
  -isystem ${NDK_ROOT}/sysroot/usr/include/x86_64-linux-android \
  -pie \
  -o  hello.c.o -c hello.c

${NDK_ROOT}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang \
  --target=x86_64-none-linux-android \
  --gcc-toolchain=${NDK_ROOT}/toolchains/x86_64-4.9/prebuilt/linux-x86_64 \
  --sysroot  ${NDK_ROOT}/platforms/android-21/arch-x86_64 \
  -pie hello.c.o -o hello
```

Some notes:


* We have to specify the Android API level (21 here) like in any other project targeting Android
* Most of the magic is done by the `--sysroot`, `--gcc-toolchain` and `--target` options.
* We have to specify `-fPIE`, a flag for *position independent code* we already seen in a previous article.

And now we can upload and run the binary on the `x86_64` simulator:

```bash
$ adb push hello /data/local/tmp
$ adb shell /data/local/tmp/hello
Hello, world
```

We can do the same thing for `arm` of course, but note how subtle the changes are to go from `x86_64` to `arm`:

```bash
export NDK_ROOT=/home/dmerej/Android/Sdk/ndk-bundle

${NDK_ROOT}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang \
  --target=armv7-none-linux-androideabi \
  --gcc-toolchain=${NDK_ROOT}/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64 \
  --sysroot=${NDK_ROOT}/sysroot \
  -isystem ${NDK_ROOT}/sysroot/usr/include/arm-linux-androideabi \
  -pie \
  -o  hello.c.o -c hello.c

${NDK_ROOT}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang \
  --target=armv7-none-linux-androideabi \
  --gcc-toolchain=${NDK_ROOT}/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64 \
  --sysroot  ${NDK_ROOT}/platforms/android-21/arch-arm \
  -pie hello.c.o -o hello

```

And if we try again:

```bash
$ adb push hello /data/local/tmp
$ adb shell /data/local/tmp/hello
Hello, world
```

Success!

# What's next

Of course, we could have use the built-in Android Studio Native plug-in directly instead of trying to guess how to invoke the compilers and linkers.

However, the goal of these blog posts is to show you how things work "under the hood", so next time we'll instead use conan and start cross-compiling C++ code. (There are a few more details we did not see because we were using C ...)

See you next time!
