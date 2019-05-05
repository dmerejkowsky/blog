---
authors: [dmerej]
slug: chuck-norris-part-5-python-cffi
date: 2018-04-07T17:58:52.242266+00:00
draft: false
title: "Let's Build Chuck Norris! - Part 5: Python and cffi"
tags: [c++, python]
---

_Note: This is part 5 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._

[Last week]({{< ref "/post/0064-let-s-build-chuck-norris-part-4-python-and-ctypes.md" >}}) we wrote Python bindings for the chucknorris library using `ctypes`.

We managed to get some Chuck Norris facts from a Python program.

On the plus side, we did not have to compile anything. Everything was done directly in Python.

There were a few issues, though:

* We had to pass the path to the `libchucknorris.so` shared library to `ctypes.cdll.LoadLibrary`.
* We had to duplicate information about parameters types of the C function inside our Python program and mistakes were easy to made.


An other way to wrap C code in Python is to use a *C extension*: that is, a Python module written in C. In this case the Python module actually takes the form of a shared library, and is thus loaded by the `python` interpreter at runtime.

There are many ways to create a Python C extension, from directly writing the C code (using the [Python C API](https://docs.python.org/3/c-api/index.html)), to generating the C code and then compile it.

In the past, I've used tools like [boost::python](https://www.boost.org/doc/libs/1_66_0/libs/python/doc/html/index.html) and [swig](http://www.swig.org/) for this task.

I only started using `cffi` recently, but I find it easier to use, and, contrary to the above tools, it is compatible with [pypy](https://pypy.org/), which is kind of awesome.


# First try with cffi

I you browse the [documentation](https://cffi.readthedocs.io/en/latest/index.html) you will see that `cffi` can be used in several *modes*. There is a *ABI mode* and an *API mode*. The ABI mode resembles the technique we used with `ctypes`,  because it involves loading `chucknorris` as a shared library.

We are going to use the *API* mode instead, where all the code is generated *using the chucknorris.h header*, which minimizes the chance of mistakes.

This means we can go back to building `chucknorris` as a static library. That way we won't have to care about the location of the library, and the  chucknorris code will be used at compile time.(Sorry for the little detour).

All we have to do is re-run cmake and ninja:

```
$ cd cpp/ChuckNorris/build/default
$ cmake -DBUILD_SHARED_LIBS=OFF ../..
$ ninja
[1/7] Building C object CMakeFiles/c_demo.dir/src/main.c.o
[2/7] Building CXX object CMakeFiles/chucknorris.dir/src/c_wrapper.cpp.o
[3/7] Building CXX object CMakeFiles/cpp_demo.dir/src/main.cpp.o
[4/7] Building CXX object CMakeFiles/chucknorris.dir/src/ChuckNorris.cpp.o
[5/7] Linking CXX static library lib/libchucknorris.a
[6/7] Linking CXX executable bin/c_demo
[7/7] Linking CXX executable bin/cpp_demo
```



Now, let's write a Python build script for our C extension using the cffi builder:

_build\_chucknorris.py_:
```python
from cffi import FFI
ffibuilder = FFI()

ffibuilder.set_source(
    "_chucknorris",
    """
    #include <chucknorris.h>
    """,
)

ffibuilder.cdef("""
typedef struct chuck_norris chuck_norris_t;
chuck_norris_t* chuck_norris_init(void);
const char* chuck_norris_get_fact(chuck_norris_t*);
void chuck_norris_deinit(chuck_norris_t*);
""")
```

* We instantiate a FFI object we call `ffibuilder`.
* In `ffibuilder.set_source()` we give the builder the name of the C extension: `_chucknorris`. It's common for C extension names to be prefixed with an underscore.
* We also give the FFI builder the C code it needs to compile the code it generates. (Here we only need to include the `<chucknorris.h>` header, but in a real project you may add things like macros or additional helper code).
* Finally we list the functions and types we want exposed in our C extension as C declarations -- directly copy/pasted from the `chucknorris.h` header -- and pass them as a string to `ffibuilder.cdef()`.

# Keeping things DRY

> "But wait a minute!", <span style="font-style:normal">I hear you say</span>. "You said cffi was better than ctypes because we did not have to duplicate information about types, but now you are telling us we still need to copy/paste C declarations inside the call to .cdef()! What gives?".

Well, it's true we usually try to keep things *DRY* when we write code, (DRY meaning "don't repeat yourself").

However, when using cffi it does not matter that much. Not following DRY is only dangerous when the duplicated code *does not change at the same time* and gets out of sync.

Let's say you break the API of your library (for instance by changing the number of arguments of a C function). If you don't reflect the change in `ffibuilder.def()`, you will get a nice compilation error, instead of a crash or segfault like we experienced with `ctypes`.

# Adding a setup.py

With that out of the way, let's add a `setup.py` file we can use while developing our bindings, install our code, and re-distribute to others:

_setup.py_:
```python
from setuptools import setup, find_packages

setup(name="chucknorris",
      version="0.1",
      description="chucknorris python bindings",
      author="Dimitri Merejkowsky",
      py_modules=["chucknorris"],
      setup_requires=["cffi"],
      cffi_modules=["build_chucknorris.py:ffibuilder"],
      install_requires=["cffi"],
)
```

Here's what the parameters do:

* `py_modules`: the list of Python modules to install. We only got one, called `chucknorris`, that will use the `_chucknorris` C extension and expose a more "Pythonic" API.
* `setup_requires`: what the `setup.py` script needs in order to build the extension.
* `cffi_modules`: the list of Python objects to be called when building the extension. Here it's the `ffibuilder` object defined in the `build_chucknorris.py` file.
* `install_requires`: the list of the dependencies of our module *once it has been built and installed*. We *also* need `cffi` at runtime, not just for compiling the extension.

Finally, we can write the implementation of the chucknorris Python module:


_chucknorris.py:_
```python
from _chucknorris import lib, ffi


class ChuckNorris:
    def __init__(self):
        self._ck = lib.chuck_norris_init()

    def get_fact(self):
        c_fact = lib.chuck_norris_get_fact(self._ck)
        fact_as_bytes = ffi.string(c_fact)
        return fact_as_bytes.decode("UTF-8")

    def __del__(self):
        lib.chuck_norris_deinit(self.c_ck)


def main():
    chuck_norris = ChuckNorris()
    print(chuck_norris.get_fact())


if __name__ == "__main__":
    main()
```

* We start by importing code from the `_chucknorris` C extension. `lib` contains what has been wrapped -- declared with `ffibuilder.cdef()` -- , and `ffi` contains various cffi helpers.
* We hide the `lib.chuck_norris_init()` and `lib.chuck_norris_deinit()` under the `__init__` and `__del__` methods. (Exactly what we did when going from the C++ constructor and destructors to the C functions, but the other way around)
* In the `get_fact()` method, we call `lib.chuck_norris_get_fact()`. `chuck_norris_get_fact()` returns a "C string", which is just a `char*` array that ends with `\0`. We pass it to `ffi.string()` to get a `bytes` object, suitable for holding this kind of data. And finally, we convert the list of bytes to a real string using `decode()`.
* Finally, when the `chucknorris.py` script is called, we use our nice Python class as if no C code ever existed :)


# Running the builder

After installing the `cffi` package, we can finally try and build the code:

```
$ python setup.py build_ext
running build_ext
generating ./_chucknorris.c
...
building '_chucknorris' extension
gcc ...
  -fPIC
  ...
  -I/usr/include/python3.6m
  -c _chucknorris.c
  -o ./_chucknorris.o
_chucknorris.c:493:14: fatal error: chucknorris.h: No such file or directory
```

What happened?

* `python setup.py build_ext` found out how to use our `ffibuilder` object.
* It generated some C code in a `_chucknorris.c` file
* It started building the `_chucknorris` extension using `_chucknorris.c` and the code we passed in `ffibuilder.set_source()` and `ffibuilder.cdef()`.
* The `ffibuilder.compile()` method knew about our old friend `-fPIC`, and about the path to the Python includes (`-I/usr/include/python3.6m`), but it could not find the `chucknorris.h` header and the compilation failed.

# Tweaking the ffibuilder

Clearly the `ffibuilder` needs to know about the chucknorris library and the chucknorris include path.

We can pass them directly to the `set_source()` method using the `extra_objects` and `include_dirs` parameters. [^1]

_build\_chucknorris.py_:
```python
import path

cpp_path = path.Path("../cpp/ChuckNorris").abspath()
cpp_build_path = cpp_path.joinpath("build/default")
ck_lib_path = cpp_build_path.joinpath("lib/libchucknorris.a")
ck_include_path = cpp_path.joinpath("include")

ffibuilder.set_source(
    "_chucknorris",
    """
    #include <chucknorris.h>

    """,
    extra_objects=[ck_lib_path],
    include_dirs=[ck_include_path],
)
...
```

Note that we use the wonderful [path.py](https://github.com/jaraco/path.py) library to handle path manipulations, which we can add to our `setup.py` file:

```python

from setuptools import setup

setup(name="chucknorris",
      version="0.1",
      ...
      setup_requires=["cffi", "path.py"],
      ...
)
```

# The missing symbols

Let's try to build our extension again:

```
$ python setup.py build_ext
running build_ext
generating ./_chucknorris.c
...
building '_chucknorris' extension
gcc ... -fPIC ... -I/usr/include/python3.6m -c _chucknorris.c -o ./_chucknorris.o
gcc ... -shared  ... -o build/lib.linux-x86_64-3.6/_chucknorris.abi3.so
```

OK, this works.

Now let's run `python setup.py develop` so that we can import the C extension directly:

```
$ python setup.py develop
...
generating cffi module 'build/temp.linux-x86_64-3.6/_chucknorris.c'
already up-to-date
...
copying build/lib.linux-x86_64-3.6/_chucknorris.abi3.so ->
...
```

Note that `setup.py develop` takes care of building the extension for us, and is even capable to skip compilation entirely when nothing needs to be rebuilt.

Now let's run the `chucknorris.py` file:

```
$ python chucknorris.py
Traceback (most recent call last):
  File "chucknorris.py", line 1, in <module>
    from _chucknorris import lib, ffi
ImportError: .../_chucknorris.abi3.so: undefined symbol: _ZNSt8ios_base4InitD1Ev
```

Damned!

That's the problem with shared libraries. `gcc` happily lets you build a shared library even if there are symbols that are not defined anywhere. It just assumes the missing symbols will be provided sometime before loading the library.

Thus, the only way to make sure a shared library has been properly built is to *actually load it from an executable* [^2].

Again we are faced with the task of guessing the library from the symbol name. Since it looks like a mangled C++ symbol, we can using `c++filt` to get a more human-readable name:

```
$ c++filt _ZNSt8ios_base4InitD1Ev
std::ios_base::Init::~Init
```

Here I happen to know this is a symbol that comes from the c++ *runtime library*, the library that contains things like the implementation of `std::string`.

We can solve the problem by passing the name of the `c++` library directly as a `libraries` parameter:

```python
ffibuilder.set_source(
    "_chucknorris",
    """
    #include <chucknorris.h>

    """,
    extra_objects=[ck_lib_path],
    include_dirs=[ck_include_path],
    libraries=["stdc++"],
```

Note: we could also have set the `language` parameter to `c++`, and invoke the C++ linker when linking `_chucknorris.so`, because the C++ linker knows where the c++ runtime library is. [^3]

Let's try again:

```
$ python setup.py develop
$ python chucknorris.py
ImportError: .../_chucknorris.abi3.so: undefined symbol: sqlite3_close
```

This one is easier: `chucknorris` depends on `libsqlite3`, so we have to link with `sqlite3` too.

In the CMakeLists.txt we wrote back in [part 2]({{< ref "/post/0062-let-s-build-chuck-norris-part-2-sqlite-and-conan.md" >}}), when we were building the `cpp_demo` executable, we just called `target_link_libraries(cpp_demo chucknorris)`. CMake knew about the dependency from the `chucknorris` target to the sqlite3 library and everything worked fine.

But we're not using the CMake&nbsp;/&nbsp;conan build system here, we are using the Python build system. How can we make them cooperate?

# The json generator

Since conan 1.2.0 there is a generator called `json` [^4] we can use to get machine-readable information about dependencies.

Here's how we can use this json file inside our ffibuilder.

First, let's add `json` to the list of conan generators:

_conanfile.txt_:
```ini
[requires]
sqlite3/3.21.0@dmerej/test

...

[generators]
cmake
json
```

Then, let's re-run `conan install`:

```
$ cd cpp/python/build/default
$ conan install ../..
...
PROJECT: Installing /home/dmerej/src/chucknorris/cpp/ChuckNorris/conanfile.txt
...
sqlite3/3.21.0@dmerej/test: Already installed!
PROJECT: Generator cmake created conanbuildinfo.cmake
PROJECT: Generator json created conanbuildinfo.json
```

This generates a `conanbuildinfo.json` file looking like this:

_build/default/conanbuildinfo.json_:
```json
{
  "dependencies": [
    {
      "version": "3.21.0",
      "name": "sqlite3",
      "libs": [
        "sqlite3",
        "pthread",
        "dl"
      ],
      "include_paths": [
        "/.../.conan/data/sqlite3/.../<id>/include"
      ],
      "lib_paths": [
        "/.../.conan/data/sqlite3/.../<id>/lib"
      ],
    }
  ]
}

```

Now we can parse the json file and pass the libraries and include paths to the `ffibuilder.set_source()` function:

_build\_chucknorris.py_:
```python
cpp_path = path.Path("../cpp/ChuckNorris").abspath()
cpp_build_path = cpp_path.joinpath("build/default")

extra_objects = []
libchucknorris_path = cpp_build_path.joinpath("lib/libchucknorris.a")
extra_objects.append(libchucknorris_path)

include_dirs = []
include_dirs.append(cpp_path.joinpath("include"))

libraries = ["stdc++"]

conan_info = json.loads(cpp_build_path.joinpath("conanbuildinfo.json").text())
for dep in conan_info["dependencies"]:
    for lib_name in dep["libs"]:
        lib_filename = "lib%s.a" % lib_name
        for lib_path in dep["lib_paths"]:
            candidate = path.Path(lib_path).joinpath(lib_filename)
            if candidate.exists():
                extra_objects.append(candidate)
            else:
                libraries.append(lib_name)
    for include_path in dep["include_paths"]:
        include_dirs.append(include_path)


ffibuilder.set_source(
    "_chucknorris",
    """
    #include <chucknorris.h>

    """,
    extra_objects=extra_objects,
    include_dirs=include_dirs,
    libraries=libraries,
)
```

And now everything works as expected:


```
$ python3 setup.py clean develop
$ python chucknorris.py
There are no weapons of mass destruction in Iraq, Chuck Norris lives in Oklahoma.
```

We can even build a pre-compiled wheel that other people can use it without need to compile the chucknorris project themselves:


_On the developer machine:_
```
$ python setup.py bdist_wheel
...
running build_ext
...
building '_chucknorris' extension
...
creating 'dist/chucknorris-0.1-cp36-cp36m-linux_x86_64.whl' and adding '.' to it
...
```

_On an other machine_:
```
$ pip install chucknorris-0.1-cp36-cp36m-linux_x86_64.whl
$ python -c 'import chucknorris; chucknorris.main()'
```

For this to work, the other user will need to be on Linux, have a compatible C++ library and the same version of Python, but as far as distribution of binaries on Linux usually go, isn't this nice?

There's an entire blog post to be written about distribution of pre-compiled Python binary modules, but enough about Python for now :)

See you next time, where we'll use everything we learned there and start [porting Chuck Norris to Android]({{< ref "/post/0073-let-s-build-chuck-norris-part-6-android-cross-compilation.md" >}}).

[^1]: `ffibuilder.set_source()` uses the same API as the [distutils Extension class](https://docs.python.org/3.6/distutils/apiref.html#distutils.core.Extension).
[^2]: This also means you should really have at least one executable to test every shared library you write, but you already knew that, right?
[^3]: Not sure what the best move is here. If you have an opinion on it, please let me know. PS: I know we could also use static linking, but I'm saving that for the part where we build ChuckNorris on Android.
[^4]: Disclaimer: the json generator feature was added by [yours truly](https://github.com/conan-io/conan/pull/2515).
