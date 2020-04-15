---
authors: [dmerej]
slug: chuck-norris-part-6-android-cross-compilation
date: 2018-06-05T10:17:17.789657+00:00
draft: false
title: "Let's Build Chuck Norris! - Part 6: Cross-compilation for Android"
tags: [c++]
---

_Note: This is part 6 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._


# Introduction

After our little detour talking about how to [wrap C++]({{< ref "/post/0064-let-s-build-chuck-norris-part-4-python-and-ctypes.md" >}}) in [Python]({{< ref "/post/0065-let-s-build-chuck-norris-part-5-python-and-cffi.md" >}}), we now are ready to tackle writing Android applications using C++ code.

We'll start with a simple challenge: try and run a simple "Hello, world" program written in C inside a simulator and on our phone.

Let's get started!

## A naive try

Let's see what happens if we naively try to run some C code on our phone.

* First, let's install the Android SDK so that we can use the `adb` tool.
* Then, let's activate the developer mode on the phone, and plug it to our laptop.

Now let's compile a simple C program:

```c
/* in hello.c */
#include <stdio.h>

int main() {
  printf("Hello, world\n");
  return 0;
}
```

```bash
$ gcc hello.c -o hello
```

And now, let's use `adb push` to copy the binary on our phone, and `adb shell` to try and run it:

(Note that `/data/local/tmp` is the only directory I found where we can run executables):


```
$ adb push hello /data/local/tmp
$ adb shell
$ cd /data/local/tmp
$ ./hello
/system/bin/sh: ./hello: not executable: 64-bit ELF file
```

Hum. What just happened ?

## CPU architectures

When you use a compiler, you get a binary file from the source code. You can think of this binary file as a list of instructions, ready to be used by a CPU.

The trick is that different CPU have different *instructions sets*.

For instance, it is very likely that the CPU you have on your laptop is a `x86_64` CPU, and that the CPU of you phone is an `armv7`. [^1]

This means that a binary you built for a `x86_64` CPU will not run on a `armv7` CPU.


## The libc

OK, but the Android SDK also comes with a simulator, and we can choose the CPU architecture.

Can't we just use a `x86_64` Android simulator ?

If we try the same thing with a `x86_64` simulator, we get an even weirder error:

```
$ adb push hello /data/local/tmp
$ adb shell
$ cd /data/local/tmp
$ ./hello
/system/bin/sh: ./hello: no such file or directory
```

The file does exist, but Android does not know how to run it. Why?


Remember when we used `LD_TRACE_LOADED_OBJECTS` back in [a previous post](
{{< ref "/post/0064-let-s-build-chuck-norris-part-4-python-and-ctypes.md#using-the-chucknorris-shared-library" >}})?

Well, if we re-run the binary we just built we can see it loads a few `.so` files:

```
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

This is tricky because by default, compilers use the  same CPU architecture and the same libc used by the operating system they run on[^2].

This is what we call "cross-compilation".

## Using the NDK to compile by hand

Google provides a set of tools know as the *NDK* in order to help us cross-compiling code for Android.

Here we are using version `r16`.

If we download and extract the NDK, here's how we can compile and link our "Hello, World" program:

```
export NDK_ROOT=/path/to/ndk

${NDK_ROOT}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang
  --target=x86_64-none-linux-android
  --gcc-toolchain=${NDK_ROOT}/toolchains/x86_64-4.9/prebuilt/linux-x86_64
  --sysroot=${NDK_ROOT}/sysroot
  -isystem ${NDK_ROOT}/sysroot/usr/include/x86_64-linux-android
  -o  hello.c.o -c hello.c

${NDK_ROOT}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang
  --target=x86_64-none-linux-android
  --gcc-toolchain=${NDK_ROOT}/toolchains/x86_64-4.9/prebuilt/linux-x86_64
  --sysroot  ${NDK_ROOT}/platforms/android-21/arch-x86_64
  -pie hello.c.o -o hello
```

Some notes:


* We have to specify the Android API level (21 here) like in any other project targeting Android
* Most of the magic is done by the `--sysroot`, `--gcc-toolchain` and `--target` options.
* We have to specify `-fPIE`, a flag that means _position independant executable_. It serves the same kind of purpose as the `-fPIC` flag we met in [a previous article]({{< ref "/post/0064-let-s-build-chuck-norris-part-4-python-and-ctypes.md#building-the-shared-library" >}}).

And now we can upload and run the binary on the `x86_64` simulator:

```
$ adb push hello /data/local/tmp
$ adb shell /data/local/tmp/hello
Hello, world
```

We can do the same thing for `arm` of course, but note how subtle the changes are to go from `x86_64` to `arm`:

```
export NDK_ROOT=/home/dmerej/Android/Sdk/ndk-bundle

${NDK_ROOT}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang
  --target=armv7-none-linux-androideabi
  --gcc-toolchain=${NDK_ROOT}/toolchains/arm-linux-androideabi-4.9/...
  --sysroot=${NDK_ROOT}/sysroot
  -isystem ${NDK_ROOT}/sysroot/usr/include/arm-linux-androideabi
  -o  hello.c.o -c hello.c

${NDK_ROOT}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang
  --target=armv7-none-linux-androideabi
  --gcc-toolchain=${NDK_ROOT}/toolchains/arm-linux-androideabi-4.9/...
  --sysroot  ${NDK_ROOT}/platforms/android-21/arch-arm
  -pie hello.c.o -o hello

```

And if we try again:

```
$ adb push hello /data/local/tmp
$ adb shell /data/local/tmp/hello
Hello, world
```

Success!

Our next objective is to run the `cpp_demo` executable we used to test the Chuck Norris library in [part 1]({{< ref "/post/0061-let-s-build-chuck-norris-part-1-cmake-and-ninja.md#the-test-program" >}}) on our phone and on the Android simulator.

Things is going to be trickier because of the `sqlite3` dependency and the fact that the code is written in C++.

But surely there is a better way to than guessing how to invoke the compilers and linkers.


# Conan to the rescue

Of course, we could have used the native plug-in of Android Studio directly.

Instead we will use Conan, the tool we talked about in [part 2]({{< ref "/post/0062-let-s-build-chuck-norris-part-2-sqlite-and-conan.md" >}}).

Using Conan is a good way to abstract the above complexity, without loosing any of the control (like depending on an IDE plug-in does).

Plus, we can apply what we learn using Conan in other contexts such as writing C++ code on iOS.

## The standalone toolchain


If you a look at the contents of the Android NDK, you'll soon realize there are lots of stuff there.

Among the cross-compiler binaries, sysroot, include directories we used in the previous section we also have a full build system based on Makefiles called `ndk-build`.

The NDK also contains support files for every Android API from 14 to 27 and every processor architecture (aarch64, arm, mips, x86, x86_64).

That's a *lot* of stuff and it takes about 3G of disk space.

However, in `build/tools` there's a bash script called `make-standalone-toolchain.sh`. Let's take a look:

>  Creates a toolchain installation for a given Android target.
>
>  The output of this tool is a more typical cross-compiling toolchain. It is
>  intended to be used with existing build systems such as autotools.

Ah-ah! Sound like what we need, especially if later on we start depending on a library built with autotools from the ChuckNorris project.


## Build requirements

It's now time to introduce a new Conan feature, the build requirements.

Basically build requirements are packages you only need when building something from sources. See the [Conan docs](https://docs.conan.io/en/latest/devtools/build_requires.html) for more information.

So, here's the plan:

* First let's have a recipe to download and extract the NDK (hopefully just once)
* Then let's have a second recipe to run the `make_standalone_toolchain` script and set up what we need to cross-compile for Android with CMake.

Note before we begin: I'll only show you a small fraction of the recipes code. This is for educational purposes: there are a lots of details I have to omit in order to keep things readable.

## The NDK recipe

Here is a simplistic recipe for the NDK:

```python
class AndroidndkConan(ConanFile):
    name = "android-ndk"
    version = "r16"
    settings = "os_build", "arch_build"
    ...

    def source(self):
        url = "https://...android-ndk-%s-linux-x86_64.zip" % self.version
        tools.download(url, "ndk.zip")
        tools.unzip("ndk.zip", keep_permissions=True)
        tools.unlink("ndk.zip")

    def package_info(self):
        tools_path = os.path.join(self.package_folder, "build", "tools")
        ...
        env_info = self.env_info
        env_info.PATH.append(os.path.join(tools_path)
```

The `source()` method does nothing but fetching and extracting the NDK.

The `package_info()` is more interesting: it adds the `build/tools` directory in the `env_info.PATH` variable. Any recipe that has the NDK package as build requirement can thus call `self.run()` to run any binary from the tools directory, since `PATH` will be set accordingly.

## The Android toolchain recipe

We can now move on to the next recipe, the Android toolchain:

```python
class AndroidtoolchainConan(ConanFile):

    name = "android-toolchain"
    lib_version = "r16"
    package_version = "r4"
    version = "%s-%s" % (lib_version, package_version)
    license = "GPL/APACHE2"
    url = "https://github.com/lasote/conan-android-toolchain"
    settings = "os", "arch", "compiler"
    build_requires = "android-ndk/r16@dmerej/test"
    ...

    def build(self):
      ...

      toolchain = get_toolchain_str(self.settings.arch)

      command = (
        "make-standalone-toolchain.sh"
          "--verbose"
          "--toolchan=%s",
          "--platform=android-%s"
        ) % (toolchain, self.settings.os.api_level)
        self.run(command)


    def package_info(self):
        sysroot = os.path.join(self.package_folder, "sysroot")

        self.env_info.CC =  ...
        self.env_info.AR = ...

        self.env_info.CFLAGS = ...
```

As you can see, we are able to run the `make-standalone-toolchain.sh` script directly with `self.run()`.

The other important part is the `package_info()` method, which :

* Set the sysroot
* Tells the consumers of the package about the path to the binaries used during compilation and linking (CC and AR)
* Set some compile flags via the `CFLAGS` variable.

Remember when we built our C binary by hand?

We can find traces of this data in the command line we used:

```
${NDK_ROOT}/.../bin/clang                  <- this is CC
  --sysroot  ${NDK_ROOT}/...               <- this is the sysroot
  --target=armv7-none-linux-androideabi \
  --gcc-toolchain=..                     | <- those are compile flags
  -pie                                  /
  hello.c.o
  -o hello
```

Note that the recipe depends on the architecture we want our compiled code to run on. This means we are going to build one `android-toolchain` package per CPU architecture. Also note that the NDK recipe has a setting to know about the Android API level.

Where can we specify all these configuration values?

## Android Profiles

There's an elegant way to solve this.

We create a global Conan profile in `~/.conan/profiles/android`:

```ini
[build_requires]
android-toolchain/r16@dmerej/test

[settings]
os=Android
os_build=Linux
os.api_level=21
compiler=clang
compiler.version=5.0

[options]
*:pic = True
```

There we define all the common settings between all the Android configurations (like the API level, the compiler and the compiler version).

Note the `*:pic` in the `[options]` section. This will make sure that everything is built with position independent code, a requirement for anything that runs on Android.

Then if we need to build form `x86_64`, we can invoke Conan this way:

```
$ conan install --profile android --setting arch=x86_64
```

All the settings from the android profile will be used, plus the `arch` we just set on the command line.


## Cross compiling sqlite3

Let's cross-compile `sqlite3` for Android:

```
$ conan create . dmerej/test --profile android --setting arch=x86_64
sqlite3/3.21.0@dmerej/test: Exporting package recipe
...
Cross-build from 'Linux:x86_64' to 'Android:x86_64'
...
Requirements
    android-toolchain/r16@dmerej/stable
Packages
    android-toolchain/r16@dmerej/test
...
sqlite3/3.21.0@dmerej/test: Calling build()
-- Android: Targeting API '21' with
      architecture 'x86_64',
      ABI 'x86_64',
      and processor 'x86_64'
...
sqlite3/3.21.0@dmerej/test: Package built
```

Done :)


## Cross compiling the chucknorris library

Let's now try to build `ChuckNorris`:

```
$ cd cpp
$ mkdir -p build/android/x86_64
$ cd build/android/x86_64
$ conan install ../../.. --profile android --setting arch=x86_64
....
Cross-build from 'Linux:x86_64' to 'Android:x86_64'
sqlite3/3.21.0@dmerej/test: Already installed!
```

OK, now we are ready to build:


```
$ cd build/android/x86_64
$ cmake -GNinja ../../..
$ ninja
-- The C compiler identification is GNU 7.3.0
-- The CXX compiler identification is GNU 7.3.0
-- Check for working C compiler: /bin/cc
-- Check for working C compiler: /bin/cc -- works
...
-- Check for working CXX compiler: /bin/c++
-- Check for working CXX compiler: /bin/c++ -- works
...
CMake Error at build/android/x86_64/conanbuildinfo.cmake:452 (message):
  Incorrect 'clang', is not the one detected by CMake: 'GNU'
```

Uh-Oh: CMake is using the default compiler `/bin/cc`. This is not going to work.


But Conan knew how to cross-compile `sqlite3` for Android! Can't we tell Conan to build chucknorris too?

## Creating a recipe for chucknorris

Of course we can! Let's go to `cpp/ChuckNorris` and run `conan new`:

```
$ conan new ChuckNorris/0.1 --source
```

Then let's edit the generated `conanfile.py` to have:


```python
from conans import ConanFile, CMake


class ChucknorrisConan(ConanFile):
    name = "ChuckNorris"
    version = "0.1"
    license = "MIT"
    url = "https://github.com/dmerejkowsky/chucknorris"
    description = "Chuck Norris does not need a description"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("cpp_demo" dst="bin", keep_path="false")
```

Note that instead of having a `source()` method to fetch the sources from a remote location (as we did for `sqlite3`), we instead use `exports_sources` to tell Conan about the sources it needs to build the package.

Also note how we copy the `cpp_demo` binary in the `package()` method. We'll use this to check that the binary we built with Conan can actually *run*.

Then we create the chucknorris package:

```
$ cd cpp/ChuckNorris
$ conan create .  dmere/test --profile android --setting arch=x86_64
ChuckNorris/0.1@dmerej/test: Exporting package recipe
...
Cross-build from 'Linux:x86_64' to 'Android:x86_64'
...
-- Build files have been written to: ...
../bin/clang++
  --target=x86_64-none-linux-android
  --gcc-toolchain=...
  -sysroot=...
  -isysroot=...
  -fPIC
  -fPIE -pie
  .../sqlite3.a
  ...
```

Well, it did build, and the commands ran by Ninja closely resemble the ones we wrote by hand in the previous section.

Let's check it runs!

```
$ cd ~/.conan/data/ChuckNorris/0.1/dmerej/test
$ cd package/<hash>/bin
$ adb push cpp_demo /data/local/tmp/
$ adb shell /data/local/tmp/cpp_demo
CANNOT LINK EXECUTABLE "/data/local/tmp/cpp_demo":
  library "libc++_shared.so" not found
```

What?


## The libc++

Remember when we talked about the `libc`? Well, for `C++` on Android there are two possible choices.

You have to choose between the `gnustl` library, or the `libc++` library, and they both come in two flavors (static or shared).

By default, our binary was compiled to link with shared version of `libc++`, hence the file name: `libc++_shared.so`.

Fortunately, we can use an other feature of Conan to help us: the `imports()` function. This function gets called before building and can be used to copy files from the dependencies packages.

Here's what we can do:

* Use `imports()` to copy `libc++_shared.so` from the `android-toolchain` package to the build directory.
* Use `keep_imports` so that the imported files do not get removed from the build directory.
* Add a `copy()` call in the `package()` method so that the `libc++_shared.so` file is present in the final package.

This is known as "repackaging" in Conan parlance.

```python
class ChucknorrisConan(ConanFile):
    ...
    keep_imports = True

    def imports(self):
        self.copy("*libc++_shared.so", dst="lib")

    def package(self):
        self.copy("bin/cpp_demo", dst="bin", keep_path=False)
        self.copy("lib/libc++_shared.so", dst="lib", keep_path=False)
```


Now we can try again, using the `LD_LIBRARY_PATH` environment variable to tell the linker where to look for the shared libraries:


```
$ conan create .  dmere/test --profile android --setting arch=x86_64
$ cd ~/.conan/data/ChuckNorris/0.1/dmerej/test
$ cd package/<hash>/
$ adb push bin/cpp_demo /data/local/tmp
$ adb push lib/libc++_shared.so /data/local/tmp/
$ adb shell
$ cd /data/local/tmp
$ LD_LIBRARY_PATH=lib ./cpp_demo
When a zombie apocalypse starts, Chuck Norris doesn't try to survive.
The zombies do.
```

Hooray!

We can also check it works on a arm phone too:

```
$ cd cpp/conan/android-toolchain
$ conan create . dmerej/test --profile android --setting arch=armv7
$ cd cpp/conan/sqlite3
$ conan create . dmerej/test --profile android --setting arch=armv7
$ cd cpp/ChuckNorris
$ conan create . dmerej/test --profile android --setting arch=armv7
$ cd ~/.conan/data/ChuckNorris/0.1/dmerej/test
# This would be a different hash since the settings have changed:
$ cd package/<hash>/
$ adb push bin/cpp_demo /data/local/tmp
$ adb push lib/libc++_shared.so /data/local/tmp/
$ adb shell
$ cd /data/local/tmp
$ LD_LIBRARY_PATH=lib ./cpp_demo
Giraffes were created when Chuck Norris uppercutted a horse.
```


# Conclusion

We finally managed to run some `C++` code directly on Android.

However, Android applications are written in Java (or Kotlin), so we still need to wrap the C++ library in Java.

See you in [part 7]({{< ref "/post/0074-let-s-build-chuck-norris-part-7-android-jna.md" >}}) for the next episode :)

[^1]: You may be using other architectures without realizing it, but don't worry too much about it.
[^2]: It's actually a *good thing*. Otherwise you won't be able to run and debug the binaries you've just compiled.
