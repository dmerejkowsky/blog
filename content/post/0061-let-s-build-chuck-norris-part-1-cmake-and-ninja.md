---
authors: [dmerej]
slug: chuck-norris-part-1-cmake-ninja
date: 2018-03-10T14:22:53.387235+01:00
draft: false
title: "Let's Build Chuck Norris! - Part 1: CMake and Ninja"
tags: [c++]
---

_Note: This is part 1 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._

# The core library

We want a `ChuckNorris` class with a `getFact()` method that returns a random Chuck Norris fact.

Let's start with a hard-coded answer for now:

_include/ChuckNorris.hpp_:
```c++
#pragma once
#include <string>

class ChuckNorris {
  public:
    ChuckNorris();
    std::string getFact();
};
```

_src/ChuckNorris.cpp_:
```c++
#include <ChuckNorris.hpp>

ChuckNorris::ChuckNorris()
{
}

std::string ChuckNorris::getFact()
{
  return "Chuck Norris can slam a revolving door.";
}
```

We have a header in `include/ChuckNorris.hpp` containing the class *declaration*, and a file in `src/ChuckNorris.cpp` containing the class *definition*.

# The test program

To make sure the library can indeed be used in other programs, let's add a `src/main.cpp` to check we manage to get the hard-coded fact:

_src/main.cpp_
```c++
#include <ChuckNorris.hpp>
#include <iostream>

int main()
{
  ChuckNorris chuckNorris;
  std::string fact = chuckNorris.getFact();
  std::cout << fact << std::endl;
  return 0;
}
```

All we have to do is run the program without arguments, and check that something gets displayed. That will probably be enough to check our library works.

# Targets

Let's enumerate what we have to do now to build everything:

* Make sure that the `include/` directory is used when we compile code in `src/`
* Build a library using `src/ChuckNorris.cpp`
* Build an executable named `cpp_demo` using `src/main.cpp` that links with the above library.

We can say we have two *targets*: a library called `chucknorris`, and an executable named `cpp_demo`:

Here's what the commands to build them look like on Linux:

```bash
# Compile the .cpp file into a .o
$ g++ -c -I include/ src/ChuckNorris.cpp -o libchucknorris.o
# Create an archive containing the .o
$ ar qc libchucknorris.a libchucknorris.o
# Run ranlib so that the archive can be used by the linker
$ ranlib libchucknorris.a
# Compile main.cpp into main.o
$ g++ -c -I include/ src/main.cpp -o main.o
# Tell g++ to link everything into an executable
$ g++ main.o libchucknorris.a -o cpp_demo
# Run the executable we've just built:
$./cpp_demo
Chuck Norris can slam a revolving door.
```

Phew!

Keeping track of all this by hand would get tedious very soon, but fortunately there are tools that can help us.

# CMake


CMake lets us describe the targets we want to build in code:


```cmake
cmake_minimum_required(VERSION 3.10)
set(CMAKE_CXX_STANDARD 11)

project(ChuckNorris)

add_library(chucknorris
    include/ChuckNorris.hpp
    src/ChuckNorris.cpp
)


target_include_directories(
  chucknorris
  PUBLIC
    "include"
)

add_executable(cpp_demo
  src/main.cpp
)

target_link_libraries(cpp_demo chucknorris)
```

The `add_library` and `add_executable` commands describe the two targets (named `chucknorris` and `cpp_demo`) and the sources used to build them, and the `target_link_libraries` command tells CMake that `cpp_demo` *depends* on `chucknorris`.

The `target_include_directories` informs CMake that there are header files in the `include` directories that should be used both when builing the library itself, but also by consumers of the library. (We used the `-I include/` flag both for building `libchucknorris.o` and `main.co`)

If the headers were used only to compile the library, we would have used the `PRIVATE` keyword, and if they were used only by consumers of the library, we would have used the `INTERFACE` keyword instead. You can read more about this in the [CMake documentation](https://cmake.org/cmake/help/latest/manual/cmake-buildsystem.7.html).

Also note how we set the `CMAKE_CXX_STANDARD` variable. This will allow us to use modern C++ features (available in C++ 11 or later) such as the `auto` keyword or raw string literals later on.

# Ninja

Now that we have described what we want to build and how, we still need to perform the build itself.

CMake does not know how to *actually* perform the build. Instead it generates files that will be used by an *other* tool. It's called a CMake *generator*.

There are plenty of generators available, but for now we'll only talk about Ninja. I've already explain why I prefer using CMake with Ninja in an [other blog post]({{< ref "post/0035-cmake-visual-studio-and-the-command-line.md" >}}).

In our first attempt, we generated all the binaries (`libchucknorris.a`, the `.o` files and the `cpp_demo` executable) directly in the current working directory. It's cleaner to have them put inside a dedicated *build folder* instead:

* We'll only have to put the build folder into our `.gitignore` file, instead of a bunch of files
* If we want to, we can have several build folders, all using the same sources, but using different compilers or flags without risking mixing incompatible binaries.

So let's create a folder named `build/default` and call CMake, asking it to use the Ninja generator. CMake uses the current working directory as the build folder, and you must specify the path to the folder containing the `CMakeLists.txt` file as the last argument on the command line:

```text
$ mkdir -p build/default
$ cd build/default
$ cmake -GNinja ../..
```

And now we use ninja to build build and run our executable from the build folder:

```text
$ cd build/default
$ ninja
[1/4] Building CXX object CMakeFiles/chucknorris.dir/src/ChuckNorris.cpp.o
[2/4] Building CXX object CMakeFiles/cpp_demo.dir/src/main.cpp.o
[3/4] Linking CXX static library libchucknorris.a
[4/4] Linking CXX executable cpp_demo
$ ./cpp_demo
Chuck Norris can slam a revolving door.
```

Done!

Note that CMake and Ninja cooperate so that you only rebuild what's need to be rebuilt.

If we change just the `main.cpp`, we just have to rebuild `main.cpp.o` and relink the `cpp_demo`:

```text
$ ninja
[1/2] Building CXX object CMakeFiles/cpp_demo.dir/src/main.cpp.o
[2/2] Linking CXX executable cpp_demo
```

But if we change `ChuckNorris.cpp`, everything *except* `main.cpp.o` needs to be rebuilt:

```text
[1/3] Building CXX object CMakeFiles/chucknorris.dir/src/ChuckNorris.cpp.o
[2/3] Linking CXX static library libchucknorris.a
[3/3] Linking CXX executable cpp_demo
```

And if we change the `CMakeLists.txt` file, Ninja will re-run CMake for us:

```text
$ ninja
[0/x] Re-running CMake...
-- Configuring done
-- Generating done
-- Build files have been written to: /path/to/build/default
...
```

That's all for the first part. Stay tuned for part 2, where we'll introduce an external dependency and get rid of the hard-coded fact.
