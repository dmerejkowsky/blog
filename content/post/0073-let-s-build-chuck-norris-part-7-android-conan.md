---
authors: [dmerej]
slug: chuck-norris-part-7-android-conan
date: 2018-06-02T10:17:17.789657+00:00
draft: true
title: "Let's Build Chuck Norris! - Part 7: Android and Conan"
tags: [c++]
---

_Note: This is part 7 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._

# standalone toolchain

Follow [the fine documentation]http://docs.conan.io/en/latest/systems_cross_building/cross_building.html#linux-windows-macos-to-android)

# build requirements

# android profiles

# cross compile deps

Personally, I prefer to keep my conan profiles in `~/.conan/profiles/android-x86_64` so that I can omit
the full path when using `conan create`.

Let's cross-compile `sqlite3` for android:

```
$ cd console-recipes/sqlite3
$ conan create . dmerej/test -p android-x86_64
```


# cross-compile chucknorris

And then cross-compile the `chucknorris` lib:

```
$ cd cpp
$ mkdir build/android/x86_64
$ conan install ../../ -p android-x86_64
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

Uh-Oh: `cmake` is just using the default compiler `/bin/cc`. This is not going to work.


But conan knew how to cross-compile `sqlite3` for android ? Can't we tell conan to build chucknorris too ?

# Creating a recipe for chucknorris

```
$ conan new ChuckNorris/0.1 --source
```

Then patch the generated files to have:

```python
from conans import ConanFile, CMake


class ChucknorrisConan(ConanFile):
    name = "ChuckNorris"
    version = "0.1"
    license = "MIT"
    url = "https://github.com/dmerejkowsky/cpp-mobile-example"
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
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["chucknorris"]
```

Note how we use `cmake.install()` in the `package` step. More on this later.


Telling conan to build our package:

```
$ cd cpp/
$ conan build . --build-folder build/default
Project: Running build()
CMake Error: Error: generator : Unix Makefiles
Does not match the generator used previously: Ninja
```

Set CMake generator in the environment. (It could be an option in the conan profile, but it's not as
easy at it seems)
TODO: as theo about this

```
$ CONAN_CMAKE_GENERATOR=Ninja conan build . --build-folder build/default
Project: Running build()
...
-- Build files have been written to: .../cpp/build/default
ninja: no work to do.
```

Success!

Let's add `export CONAN_CMAKE_GENERATOR` in our `~/.zshrc` file so that we don't forget.

And now we can try a cross-compilation build:

```
$ conan install . --profile android-x86_64 --install-folder build/android/x86_64
$ conan build . --build-folder build/android/x86_64
```

TODO: had to patch the conanfile.py to have:

```python
    def configure(self):
        # TODO: ask theo why
        # taken fro sqlite3 recipe
        del self.settings.compiler.libcxx
```

# Running cross-compiled code


```
$ cd build/android/x86_64
$ adb push lib/libchucknorris.-o /data/local/tmp/
$ adb pusd bin/cpp-demo /data/local/tmp
$ adb shell
$ cd /data/local/tmp
$ LD_LIBRARY_PATH=. ./cpp-demo
# oups
CANNOT LINK EXECUTABLE "./cpp_demo": library "libc++_shared.so" not found
S adb push android-toolchain/x86_64-linux-android/lib64/libc++_shared.so /data/local/tmp/
$ LD_LIBRARY_PATH=. ./cpp-demo
# Success !
```
