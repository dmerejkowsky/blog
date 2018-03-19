---
authors: [dmerej]
slug: chuck-norris-part-2-sqlite-conan
date: 2018-03-18T14:29:21.238943+00:00
draft: false
title: "Let's Build Chuck Norris! - Part 2: SQLite and conan"
tags: [c++]
---


_Note: This is part 2 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._


In the previous episode we wrote a simple C++ library that returned a hard-coded Chuck Norris fact.

It's now time to put several Chuck Norris facts in a database, and select one at random when asked.

We are going to use [sqlite](https://www.sqlite.org/index.html) for that.

First, let's adapt our class declaration:

*include/ChuckNorris.hpp*:
```c++
#include <string>

#include <sqlite3.h>

class ChuckNorris
{
  public:
    ChuckNorris();
    // Make sure you cannot copy Chuck Norris
    ChuckNorris(ChuckNorris const&) = delete;
    ChuckNorris(ChuckNorris &&) = delete;
    ChuckNorris& operator=(ChuckNorris const&) = delete;
    ChuckNorris& operator=(ChuckNorris &&) = delete;
    ~ChuckNorris();

    std::string getFact();

  private:
    sqlite3* _db;
    // Note: in modern C++ code we would not have a raw pointer like this,
    // and use something like unique_ptr, but this blog post is about building
    // stuff :)
};
```

Then, it's time to adapt the `ChuckNorris.cpp` file:

In the constructor, we open an in-memory database and fill it with lots of facts.

Then, in the `getFact()` method, we run a simple SQL query:


*src/ChuckNorris.cpp*:
```c++
// Note: Error handling omitted for brevity.

#include <sqlite3.h>

ChuckNorris::ChuckNorris()
{
  sqlite3_open(":memory:", &_db);

  auto const sql = R"(
CREATE TABLE chucknorris(id PRIMARY_KEY, fact VARCHAR(500));
INSERT INTO chucknorris (fact) VALUES
  ("Chuck Norris can slam a revolving door.");
INSERT INTO chucknorris (fact) VALUES
  ("Chuck Norris can kill two stones with one bird.");
  ...
  )";

  auto res = sqlite3_exec(db, sql, 0, 0, nullptr);
}

std::string ChuckNorris::getFact()
{
  sqlite3_stmt* statement;
  sqlite3_prepare_v2(_db,
      R"(SELECT fact FROM chucknorris ORDER BY RANDOM() LIMIT 1;)",
      -1, &statement, 0);
  rc = sqlite3_step(statement);
  auto sqlite_row = sqlite3_column_text(statement, 0);
  auto row = reinterpret_cast<const char*>(sqlite_row);
  auto res = std::string(row);
  sqlite3_finalize(statement);
  return res;
}
```


Now let's try and compile this!


# Third party libraries

Since we are not the authors of the `sqlite` library, we say it is a *third-party* library. (As opposed to the `chucknorris` library we just wrote).

There are a lot of ways of adding a third-party dependency to a C++ program, from simply adding the sources to the project files, to installing them "in the system" (using `homebrew` on macOS or the package manager of your distribution on Linux).

In this article we will use a package manager called [conan](https://conan.io) that will install the `sqlite3` package somewhere in our home directory (called a *cache*).

This means we won't need any administrative privileges (as opposed to installing the `sqlite3` library in the system), but also that the library will usable from multiple C++ projects (as opposed to adding the sources of `sqlite3` inside our source folder).

Using conan will come in handy when we start cross-compiling things later, but I'm getting ahead of myself.

# Adding the dependency by hand

Let's start by doing the work "by hand" before we talk about how conan works.

## Building sqlite3

First, we go to [the download page of the sqlite3 project](https://www.sqlite.org/download.html).

We then fetch the "almagation" archive, and extract it:

```console
$ cd $HOME
$ mkdir -p 3rdpart/sqlite
$ cd 3rdpart/sqlite
$ wget https://www.sqlite.org/2018/sqlite-amalgamation-3220000.zip
$ unzip sqlite-amalgamation-3220000.zip
$ cd sqlite-amalgamation-3220000
$ ls
$ shell.c  sqlite3.c  sqlite3.h  sqlite3ext.h
```

OK, we just have a `sqlite3.c` to build and a `sqlite3.h` header that we can include.

Let's build a static library:

```console
$ gcc -c sqlite3.c -o sqlite3.o
$ ar qf libsqlite3.a sqlite3.o
$ ranlib libsqlite3.a
```

And, just to clean things up, let's create a `lib` and `include` folder:

```console
$ mkdir include lib
$ mv libsqlite3.a lib/
$ mv sqlite3.h include/
```

Now we have to adapt the `CMakeLists.txt` in the Chuck Norris sources to use our newly built library.

## Finding and using the sqlite3 library

In CMake parlance, `sqlite3` is no longer a "regular" target, since it does not know how it was built.

So we need to create an *imported* target, and set the `IMPORTED_LOCATION` and `INTERFACE_INCLUDE_DIRECTORIES` properties on it:

```cmake
project(ChuckNorris)

# ...

add_library(sqlite3 STATIC IMPORTED)
set_target_properties(sqlite3
  PROPERTIES
  IMPORTED_LOCATION /path/to/sqlite3-<version>/lib/libsqlite3.a
  INTERFACE_INCLUDE_DIRECTORIES /path/to/sqlite3-<version>/include
)

add_library(chucknorris
  # ...
)
```

This allows us to use `target_link_libraries` to add a dependency between our `ChuckNorris` library and the imported target, the same way we did to link `cpp_demo` with `ChuckNorris`:

```cmake
target_link_libraries(chucknorris sqlite3)
```

Let's build the ChuckNorris project again:

```console
$ cd build/default
$ cmake -GNinja ../..
$ ninja -v
Build CXX object ChuckNorris.cpp.o
/bin/c++
  ../../src/ChuckNorris.cpp
  -I../../include
  -isystem /path/to/sqlite-<version>/include
  -o ChuckNorris.cpp.o
  ...
Linking CXX executable cpp_demo
/bin/c++
  main.cpp.o
  -o cpp_demo
  libchucknorris.a
  /path/to/sqlite-<version>/lib/sqlite3.a
```

You can see that CMake added the include path of sqlite3 in a `-isystem` flag[^1] when compiling `ChuckNorris.cpp`, and that it added the `libsqlite3.a` file when linking the `cpp_demo` executable.

On my machine, I still got a build failure:

```console
Linking CXX executable cpp_demo
FAILED: cpp_demo
/bin/c++
  main.cpp.o
  -o cpp_demo
  libchucknorris.a
  /path/to/sqlite-<version>/libsqlite3.a

libsqlite3.a(sqlite3.o): In function `pthreadMutexAlloc':
sqlite3.c:(.text+0x4275): undefined reference to `pthread_mutexattr_init'
...
libsqlite3.a(sqlite3.o): In function `unixDlOpen':
sqlite3.c:(.text+0x10bd8): undefined reference to `dlopen'
```

What's going on?

Turns out that, on Linux at least, sqlite3 depends on two other libraries, namely `pthread` and `dl`. (This is common enough that I was able to guess the name of the libraries from the names of the missing symbols in the error message)

We can fix our compilation failure by telling CMake about the dependency from `sqlite3`  to `pthread` and `dl`:


```cmake
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  set_target_properties(sqlite3
    PROPERTIES
      INTERFACE_LINK_LIBRARIES "dl;pthread"
   )
endif()
```

```console
$ ninja -v
/bin/c++
  main.cpp.o
  -o cpp_demo
  libchucknorris.a
  /path/to/sqlite-<version>/lib/libsqlite3.a
  -ldl
  -lpthread
```

That was not trivial, and we had to hard-code the location of the sqlite3 sources.

Let's now see how conan can help us using sqlite3 more easily.


# Installing conan

Conan is written in Python and you can install it with `pip`:

```console
$ python3 -m pip install conan --user
```

Afterwards, you should add the directory where the `conan` binary has been installed in your `PATH`

* Linux: `export PATH="${HOME}/.local/bin:${PATH}"`
* macOS: `export PATH="${HOME}/Library/Python3.x/bin:${PATH}"`
* Windows: nothing to do ;-)

Conan lets you write *recipes* and upload *binary packages*.

A recipe is a piece of Python code that is used to build a package; and a package is simply an archive containing pre-compiled binaries.

In the conan world, any user can publish recipes and binary packages for any library. (Many package managers use a "first come, first served" approach to package names, but not conan).

As many other package managers, conan can look for packages in multiple locations called *remotes*: all you need is to host a [conan server](http://docs.conan.io/en/latest/uploading_packages/running_your_server.html) somewhere.

By default, conan comes with the `conan-center` remote pre-configured.

# Creating a conanfile.txt

Conan uses a simple configuration file format where you can specify the dependencies and some "generators":

```cfg
[requires]
sqlite3/3.21.0@bincrafters/stable

[generators]
cmake
```

The string `sqlite3/3.21@bincrafters/stable` is called a *reference*.

There's the name: `sqlite3`, the version: `3.21`, a user: `bincrafters` and a channel: `stable`.

You can think of channels as branches: the `stable` channel indicates that the recipes and binary packages have come through at least minimal quality assurance. (This is true for any package coming from the `conan-center` remote inside the stable channel).

The `cmake` generator tells conan to generate some files that contain information about the dependencies that are usable by CMake.

Here's how to invoke conan:

<pre>
$ cd build/default
$ conan install ../..
sqlite3/3.21.0@bincrafters/stable: Not found in local cache, looking in remotes...
sqlite3/3.21.0@bincrafters/stable: Trying with 'conan-center'...
...
PROJECT: Installing /path/to/conanfile.txt
Requirements
    sqlite3/3.21.0@bincrafters/stable from 'conan-center'
Packages
    sqlite3/3.21.0@bincrafters/stable:6ae331b72e7e265ca2a3d1d8246faf73aa030238
PROJECT: Retrieving package 6ae331b72e7e265ca2a3d1d8246faf73aa030238
...
PROJECT: Generator cmake created conanbuildinfo.cmake
</pre>

Several things happened here:

* First conan looked for the package in the local cache and did not find it.

* It used a *remote*  called `conan-center` and found a compatible package there with a certain ID (`6ae331b72e7e265ca2a3d1d8246faf73aa030238`).

* Then it downloaded the binary package from the remote and stored it in the cache.

* Finally, it generated a file called `conanbuildinfo.cmake` in the build folder.

# Adapt CMakeLists.txt

We can then revert our changes in the `CMakeLists.txt` file and instead include the file conan generated for us, using the `include()` CMake function and the predefined CMake variable `CMAKE_BINARY_DIR` that points to the build folder:

```cmake
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
```

Then we invoke the `conan_basic_setup()` method and refer to the targets defined by conan using the `CONAN_PKG::` prefix:

```cmake
project(ChuckNorris)
set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# ...

target_link_libraries(chucknorris CONAN_PKG::sqlite3)
```

We can now call `cmake` and `ninja` as we did in the end of the previous part:

```console
$ cmake -GNinja ../..
...
-- Conan: Using cmake targets configuration
-- Library sqlite3 found /home/dmerej/.conan/data/.../lib/libsqlite3.a
...
$ ninja
[1/3] Building CXX object CMakeFiles/chucknorris.dir/src/ChuckNorris.cpp.o
[2/3] Linking CXX static library lib/libchucknorris.a
[3/3] Linking CXX executable bin/cpp_demo
$ ./bin/cpp_demo
The easiest way to determine Chuck Norris's age is to cut him
in half and count the rings.
$ ./bin/cpp_demo
If, by some incredible space-time paradox, Chuck Norris would ever fight
himself, he'd win. Period.
```

Seems to work!

In the next article, we'll write a C wrapper on top of our C++ API and use it to implement a `chucknorris` module in Python.

See you soon :)



[^1]: The `-isystem` flag works almost like the `-I` flag. You can find all about the gory details in the gcc man page.
