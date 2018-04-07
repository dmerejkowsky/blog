---
authors: [dmerej]
slug: chuck-norris-part-4-python-ctypes
date: 2018-03-31T12:44:43.054886+00:00
draft: false
title: "Let's Build Chuck Norris! - Part 4: Python and ctypes"
tags: [c++, python]
---


_Note: This is part 4 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._

# Static and shared libraries

C and C++ libraries come in two forms: static and shared.

In both cases, a library is collection of names (the symbols) and executable code. The difference between static and shared libraries is how those are used, for instance by an executable.

The code from a static library is **directly integrated** into the program: the compiler will take copies of the code the program uses from the static library and make it part of the program.

On the other hand, the code in a shared library is only **referenced by** the program. When the program is launched, the operating system will try and find the code to run in the shared library file.

We says the code in the static library is used *at compile time* whereas the code of a shared library is used *at runtime*.

For this reason, static libraries are also called *archive libraries*, and shared library are also called *dynamic libraries*.

Static and shared libraries usually have different extensions depending on the platform:

| platform | static | shared    |
|----------|--------|-----------|
| Linux    | .a     | .so       |
| macOS    | .a     | .dylib    |
| Windows  | .lib   | .dll [^1] |

So, which type of library do we need to write bindings in Python ?

{{<note>}}
From now on, everything takes place on a **Linux** machine. There are some differences when using macOS or Windows, but for the sake of simplicity I will only deal with one platform here.
We will also use **Python3** only. Again, in Python2 things are a little different, but let's keep things simple.
{{</note>}}

Since we are using Python as a *program* (the `/usr/bin/python3` binary), it's obviously too late to do anything at compile time. So let's build a shared library and see what we can do at runtime, shall we?


# Building the shared library


When we described the chucknorris library in our CMakeList.txt earlier, we did not specify its type.

The type of the library used in this case is controlled by a variable called `BUILD_SHARED_LIBS` which is `OFF` by default. So, let's re-run CMake, setting this variable to `ON` instead.


<pre>
$ cd build/default
$ cmake -GNinja -DBUILD_SHARED_LIBS=ON ../..
$ ninja
...
-- Library sqlite3 found /.conan/data/sqlite3/3.21.0/bincrafters/...libsqlite3.a
...
[1/7] Building C object CMakeFiles/c_demo.dir/src/main.c.o
[2/7] Building CXX object CMakeFiles/chucknorris.dir/src/c_wrapper.cpp.o
[3/7] Building CXX object CMakeFiles/cpp_demo.dir/src/main.cpp.o
[4/7] Building CXX object CMakeFiles/chucknorris.dir/src/ChuckNorris.cpp.o
[5/7] Linking CXX shared library lib/libchucknorris.so
FAILED: lib/libchucknorris.so
: && /bin/c++ ...
  -o lib/libchucknorris.so
  ChuckNorris.cpp.o
  c_wrapper.cpp.o
  ...
  libsqlite3.a
  ..
/bin/ld: libsqlite3.a(sqlite3.o): relocation R_X86_64_PC32
against symbol `sqlite3_version` can not be used when making a shared object;
recompile with -fPIC
</pre>

The link fails.

What's going on here is that we are trying to incorporate a static library (`libsqlite3.a`) inside a shared one. Most of the time this works fine, but not on Linux.

The compiler tells us what needs to be done: we have to recompile `libsqlite3.a` with `-fPIC`.

Here's what `man gcc` has to say about `fpic`:

<pre>
-fpic
  Generate position-independent code (PIC) suitable for use in a shared library.
</pre>


Fair enough, let's try to rebuild `sqlite3` by generating position-independent code.


# Patching a conan recipe

The first step is to see if we can rebuild sqlite3 ourselves.

We will be using a different user name and channel. (*@dmerej/test* instead of *@bincrafters/stable*). As we explained earlier, conan is decentralized, so copying and modifying other people's recipes in order to satisfy your requirements is possible and even encouraged.

Let's fetch the recipe from the remote:

<pre>
$ conan copy sqlite3/3.21.0@bincrafters/stable dmerej/test
Downloading conan_sources.tgz
[==================================================] 706B/706B
Copied sqlite3/3.21.0@bincrafters/stable to sqlite3/3.21.0@dmerej/test
Copied sources sqlite3/3.21.0@bincrafters/stable to sqlite3/3.21.0@dmerej/test
</pre>

Here conan looked for the recipe in the remote and created a copy with a different name, but still inside the conan cache.

Then we copy the sources from the cache and put them in a `conan/sqlite3` folder next to the C++ code:

<pre>
$ cd ChuckNorris/cpp
$ mkdir -p conan/sqlite3
$ cd conan/sqlite3
$ cp -rv ~/.conan/data/sqlite3/3.21.0/bincrafters/stable/export/* .
'../conanfile.py' -> './conanfile.py'
'../conanmanifest.txt' -> './conanmanifest.txt'
'../LICENSE.md' -> './LICENSE.md'
</pre>

Let's try to build the package ourselves:

<pre>
$ conan create . dmerej/test
sqlite3/3.21.0@dmerej/test: Exporting package recipe
sqlite3/3.21.0@dmerej/test: A new conanfile.py version was exported
...
sqlite3/3.21.0@dmerej/test: Installing package
..
sqlite3/3.21.0@dmerej/test: Attempting download of sources from:
  https://www.sqlite.org/2017/sqlite-amalgamation-3210000.zip
...
sqlite3/3.21.0@dmerej/test: Calling build()
CMake Error: The source directory "..." does not appear to contain CMakeLists.txt.
</pre>

Turns out we need to also copy some files from the `export_source` folder:

<pre>
$ cp -rv ~/.conan/data/sqlite3/3.21.0/bincrafters/stable/export_source/* .
'../CMakeLists.txt -> './CMakeLists.txt'
'../FindSQLite3.cmake' -> './FindSQLite3.cmake'
</pre>

And now we can build:

<pre>
$ conan create . dmerej/test
sqlite3/3.21.0@dmerej/test: Exporting package recipe
sqlite3/3.21.0@dmerej/test: A new conanfile.py version was exported
...
sqlite3/3.21.0@dmerej/test: Installing package
..
sqlite3/3.21.0@dmerej/test: Attempting download of sources from:
  https://www.sqlite.org/2017/sqlite-amalgamation-3210000.zip
...
sqlite3/3.21.0@dmerej/test: Calling build()
...
[1/2] Building C object CMakeFiles/sqlite3.dir/sources/sqlite3.o
[2/2] Linking C static library lib/libsqlite3.a
...
sqlite3/3.21.0@dmerej/test: Package '6ae331b72e7e265ca2a3d1d8246faf73aa030238' built
...
sqlite3/3.21.0@dmerej/test: Calling package()
sqlite3/3.21.0@dmerej/test package(): Copied 1 '.cmake' files: FindSQLite3.cmake
sqlite3/3.21.0@dmerej/test package(): Copied 2 '.h' files: sqlite3.h, sqlite3ext.h
sqlite3/3.21.0@dmerej/test package(): Copied 1 '.a' files: libsqlite3.a
...
sqlite3/3.21.0@dmerej/test: Package '6ae331b72e7e265ca2a3d1d8246faf73aa030238' created
</pre>

Let's sum up what happened:

* Conan fetched the sources from `sqlite.org`
* It called `CMake` using the `CMakeLists.txt` we copied from `export_source`
* It built the CMake project using a function named `build()`
* It copied some files using a function named `package()`.

This is roughly what we did earlier when we built sqlite by hand.

Let's take a closer look at the conan source files:

_CMakeList.txt_:
```cmake
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_library(sqlite3 sources/sqlite3.c)
```

_conanfile.py_:
```python

class ConanSqlite3(ConanFile):
    name = "sqlite3"
    version = "3.21.0"
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False]}
    ...

    def source(self):
        base_url = "https://www.sqlite.org/" + self.year
        ...
        download_url = "{0}/{1}.{2}".format(base_url, archive_name, archive_ext)
        tools.get(download_url)

    def build(self):
        cmake = CMake(self)
        ...
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(...)
```

The conan recipe is just a Python class that derives from the `ConanFile` class.

It contains the `source()`, `build()` and `package()` methods used to fetch the sources, build the package, and copy the relevant files we saw mentioned in the previous console output.

It uses a `CMake` class that knows how to run `cmake`.

Finally, the class contains a few attributes. `name` and `version` are self-explanatory, but we have to talk about the `settings` and `options`.

In both cases, settings and options are variables the consumers of the package can set. The settings cannot have default values, and if a setting changes, a different package must be produced. This is why the compiler (think `gcc` versus `Visual Studio`) is a setting. Settings are set globally, usually inside a profile, and apply to all the recipes. Options are different: they can have default values, they can be set package per package, and they have a pre-defined list of possible values.

We can see the `conanfile.py` already defines a `shared` option that can be true or false. We do not really want a shared `sqlite3` library, we want a static `sqlite3` library but built with position independent code.

There are several ways to do this. One of them is to introduce a new option called `pic`.

CMake knows how to convert the abstract concept of "position independent code" into concrete compiler flags such as `-fPIC` for gcc, so we just have to set the correct CMake variable:

```python

class ConanSqlite3(ConanFile):

    settings = "os", "compiler", "arch", "build_type"
    options = {
      "shared": [True, False],
      "pic": [True, False],
    }


    def build(self):
        cmake = CMake(self)
        if self.options.shared:
            cmake.definitions["BUILD_SHARED_LIBS"] = "ON"
        if self.options.pic:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"
        ...

```


So now we can re-create the `sqlite3` package:

<pre>
$ conan create --option 'pic=True' . dmerej/test
</pre>

Finally, we can change the `conanfile.txt` in `cpp/ChuckNorris` to reference our newly built package:

_conanfile.txt_:
```ini
[requires]
sqlite3/3.21.0@dmerej/test
```

# Using the chucknorris shared library

Let's re-run `conan install`, using the `--option` command line flag again, and see if we can manage to build chucknorris the way we want.

Note that we prefix the `pic=True` option by the name of the package we want to apply the option on. If we did not do that, `conan` would have tried to set the option on *every* package.

<pre>
$ cd build/default
$ conan install ../.. --option 'sqlite3:pic=True'
$ cmake -GNinja -DBUILD_SHARED_LIBS=ON ../..
$ ninja
[1/7] Building C object CMakeFiles/c_demo.dir/src/main.c.o
[2/7] Building CXX object CMakeFiles/chucknorris.dir/src/c_wrapper.cpp.o
[3/7] Building CXX object CMakeFiles/cpp_demo.dir/src/main.cpp.o
[4/7] Building CXX object CMakeFiles/chucknorris.dir/src/ChuckNorris.cpp.o
[5/7] Linking CXX shared library lib/libchucknorris.so
[6/7] Linking C executable bin/c_demo
[7/7] Linking CXX executable bin/cpp_demo
</pre>


Success!

Side note: specifying the option about `sqlite3` each time we call `conan` is a bit tedious, but we can just specify the option directly in the `conanfile.txt`:

```ini
[requires]
sqlite3/3.21.0@dmerej/test

[options]
sqlite3:pic = True
```

Anyway, we said earlier that it was the operating system that took care of loading code from the shared library at runtime. On Linux, this is done by a special shared library called `ld-linux.so`.

We can thus check that the `libchucknorris.so` file does get loaded when we run the `cpp_demo` executable, by asking `ld.so` to output debug information about the files it loads [^3]:

<pre>
$ cd build/default
$ export LD_TRACE_LOADED_OBJECTS=1
$ ./bin/cpp_demo
./bin/cpp_demo
	linux-vdso.so.1 (0x00007ffe07395000)
	libchucknorris.so => .../build/default/lib/libchucknorris.so (0x00007f5f4c43e000)
    ...
	libpthread.so.0 => /usr/lib/libpthread.so.0 (0x00007f5f4c220000)
	libdl.so.2 => /usr/lib/libdl.so.2 (0x00007f5f4c01c000)
    ...
Chuck Norris knows Victoria's secret
</pre>

Our friends `libpthread.so` and `libdl.so` we had to take care of when we linked with `sqlite3` by hand are involved, and we can see the full path of the ChuckNorris lib inside our build folder.


# Using ctypes

The Python standard library contains a module called `ctypes` that allows to do what `ld.so` does, but using Python code.

The documentation says we can use `ctypes.cdll.LoadLibrary` to get a "handle" from the `.so`, and then use the symbols in the shared library simply by calling methods with the right names on the handle.

Let's try:

```python
handle = ctypes.cdll.LoadLibrary("build/default/lib/libchucknorris.so")
ck = handle.chuck_norris_init()
fact = handle.chuck_norris_get_fact(ck)
print(fact)
```

<pre>
$ python ck.py
zsh: segmentation fault (core dumped)  python ck.py
</pre>

Whoops :/

Actually for this to work we have to specify the types of the parameters and return values for every method we call, like this:

```python
handle = ctypes.cdll.LoadLibrary("build/default/lib/libchucknorris.so")
handle.chuck_norris_init.restype = ctypes.c_void_p
handle.chuck_norris_get_fact.restype = ctypes.c_char_p
handle.chuck_norris_get_fact.argtypes = [ctypes.c_void_p]
ck = handle.chuck_norris_init()
fact = handle.chuck_norris_get_fact(ck)
print(fact)
```

<pre>
$ python ck.py
b'When Chuck Norris enters a rodeo the bull has to try and last 8 seconds.'
</pre>

Almost there: we still have get rid of the `b'` prefix.

`ctypes` can't really assume a `char *` in C code contains text, so the `c_char_p` type has been translated to a `bytes` object, suitable for representing binary data.

Assuming we were careful and only inserted valid UTF-8 encoded text in our sqlite3 database, we can call `.decode(UTF-8)` in our Python code, though:

```python
fact_as_bytes = handle.chuck_norris_get_fact(ck)
fact_text = fact_as_bytes.decode("UTF-8")
print(fact_text)
```

<pre>
$ python ck.py
When Chuck Norris enters a rodeo the bull has to try and last 8 seconds.
</pre>

And we're done

In the next article, we'll show a more robust method to write our Python bindings. Stay tuned!

[^1]: Actually, on Windows when you want to link with a shared library, you use both a `.lib` when linking and a `.dll` at runtime. It's confusing, I know.
[^2]: This file is the reason sometimes people on the internet will tell you to run `ldconfig` after installing a shared library: it's used to rebuild the cache.
[^3]: This is the technique used by `ldd`, by the way.
