---
authors: [dmerej]
slug: chuck-norris-part-7-android-conan
date: 2018-06-02T10:17:17.789657+00:00
draft: true
title: "Let's Build Chuck Norris! - Part 7: Android and Conan"
tags: [c++]
---

_Note: This is part 7 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._


# The standalone toolchain

If you a look at the contents of the Android NDK, you'll soon realize there are lots of stuff there.

Among the cross-compiler binaries, sysroot, include directories we saw [last week]() we also have a full build system based on Makefiles called `ndk-build`.

The NDK also contains support files for every Android API from 14 to 27 and every processor architecture (aarch64, arm, mips, x86, x86_64).

That's a *lot* of stuff and it takes about 3G of disk space.

However, in `build/tools` there's a bash script called `make-standalone-toolchain.sh`. Let's take a look:

```
Creates a toolchain installation for a given Android target.

The output of this tool is a more typical cross-compiling toolchain. It is
indended to be used with existing build systems such as autotools.
```

Ah-ah!


# Build requirements

It's now time to introduce a new conan feature, the build requirements.

Basically build requirements are packages you need only when building something from sources. See the [conan docs](https://docs.conan.io/en/latest/devtools/build_requires.html) for more information.

So, here's the plan:

* First let's have a recipe to download and extract the NDK (hopefully just once)
* Then let's have a second recipe to run the `make_standalone_toolchain` script and set up what we need to cross-compile for android.

Note before we begin: I'll only show you a small fraction of the recipes code. This is for educational purposes: there are a lots of details I have to omit to keep this post understandable.

# The NDK recipe

Here goes a simplistic recipe for the NDK:

```python
class AndroidndkConan(ConanFile):
    name = "android-ndk"
    version = "r16"
    settings = "os_build", "arch_build"
    ...

    def source(self):

        urls = {
          ...
            "Linux_x86_64":
              ["https://...android-ndk-%s-linux-x86_64.zip" % self.version,
              "b7dcb08fa9fa403e3c0bc3f741a445d7f0399e93"]
        }


        tools.download(url, "ndk.zip")
        tools.check_sha1("ndk.zip", sha1)
        tools.unzip("ndk.zip", keep_permissions=True)
        unlink("ndk.zip")

   def package_info(self):
        tools_path = os.path.join(self.package_folder, "build", "tools")
        ...
        self.env_info.PATH.append(os.path.join(tools_path)
        self.env_info.CMAKE_ANDROID_STANDALONE_TOOLCHAIN = self.package_folder
```

The `source()` method does nothing but fetching and extracting the NDK.

The `package_info()` is more interesting:

* First, it add the `build/tools` folder in the `env_info.PATH` variable. This means than any recipe that has the NDK package as build requirements will be able to run any tool from the `build/tools` folder using simply `self.run()`.
* Second, it sets the `CMAKE_ANDROID_STANDALONE_TOOLCHAIN` CMake variable. This means that any consumer of the NDK package built with CMake will be built with a CMake variable called `CMAKE_ANDROID_STANDALONE_TOOLCHAIN` pointing to the directory the NDK was extracted. (`self.package_folder`).

# The Android toolchain recipe

We can now move one to the next recipe, the Android toolchain:

```python
class AndroidtoolchainConan(ConanFile):

    name = "android-toolchain"
    lib_version = "r16"
    package_version = "r4"
    version = "%s-%s" % (lib_version, package_version)
    license = "GPL/APACHE2"
    url = "https://github.com/lasote/conan-android-toolchain"
    settings = "os", "arch", "compiler"
    ...

    def build(self):
      ...

      toolchain = get_toolchain_str(self.settings.arch)

      command = (
        "make-standalone-toolchain.sh"
          "--verbose"
          "--toolchan=%s",
          "--platform=android-%s"
        ) % (toolchain, self.settings.os.api_level
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
* Tells them about the path to the binaries used during compilation and linking (CC and AR)
* Set some compile flags via the `CFLAGS` variable.

Remember when we built our C binary by hand?

Well we kind find traces of this data in the command line we used:

```
${NDK_ROOT}/.../bin/clang                  <- this is CC
  --sysroot  ${NDK_ROOT}/...               <- this is the sysrot
  --target=armv7-none-linux-androideabi \
  --gcc-toolchain=..                     | <- those are compile flags
  -pie                                  /
  hello.c.o
  -o hello
```

Note that the Android toolchain package depends on the architecture we want our compiled code to run on.

This means we are going to need one Android toolchain package per CPU architecture.

Also note that the NDK recipe has a setting to know about the Android API level.

We are going to specify all these configuration values somewhere.

# Android Profiles

There's an elegant way to solve this.

Fist, create a global conan profile in `~/.conan/profiles/android`:

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
*:pic = true
```

There we define all the common settings between all the android configurations (like the API level, the compiler and the compiler version).

Note the `*:pic` in the `[options]` section. This will make sure that everything is built with position independent code (a requirement for anything that runs on Android)

Then if we need to build form `x86`, we can invoke conan this way:

```
$ conan install --profile android --setting arch=x86
```

All the settings from the android profile will be used, plus the `arch` we just set on the command line.


# Cross compiling sqlite3

Let's cross-compile `sqlite3` for android:

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


# Cross compiling the `chucknorris` lib:

Let's now try to build `ChuckNorris`:

```
$ cd cpp
$ mkdir -p build/android/x86_64
$ cd build/android/x86_64
$ conan install ../../ --profile android --setting arch=x86_64
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


But conan knew how to cross-compile `sqlite3` for android? Can't we tell conan to build chucknorris too ?

# Creating a recipe for chucknorris

Of course we can! Let's go to `cpp/ChuckNorris` and run `conan new`:

```
$ conan new ChuckNorris/0.1 --source
```

Then patch the generated files to have:


{{< highlight python "hl_lines=14" >}}
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

{{</ highlight >}}

Note how we use `exports_sources` to tell conan the sources it needs to build the package are right next to the `conanfile.py`, as opposed to on a remote git server.

Also note how we copy the `cpp_demo` binary in the `package()` method. We'll use this to check that the binary we built with conan can actually *run* on a simulator.

(It's the same goal than in the previous article, except this time the program is written in C++ and has an external dependency).


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

Well, it did build, and the commands ran by Ninja closely resemble the ones we wrote by hand in the previous article.

Let's check it runs!

```
$ cd ~/.conan/data/ChuckNorris/0.1/dmerej/test
$ cd package/<hash>/bin
$ adb push cpp_demo /data/local/tmp/
$ adb shell /data/local/tmp/cpp_demo
CANNOT LINK EXECUTABLE "/data/local/tmp/cpp_demo":
  library "libc++_shared.so" not found
```

Wat?


# The libc++

Remember when we talked about the `libc`? Well, for `C++` on Android there are two possible choices.

You have to choose between the `gnustl` library, or the `libc++` library, and they both come in two flavors (static or shared).

By default, our binary was compiled to link with shared version of `libc++`, hence the file name: `libc++_shared.so`.

Fortunately, we can use an other feature of conan to help us: the `imports()` function.

This function gets called before building and can be used to copy files from the dependencies.

Here's what we can do:

* Use `imports()` to copy `libc++_shared.so` from the `android-toolchain` package to the build directory.
* Use `keep_imports` so that the imported files do not get removed from the build dir.
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

We managed to run some `C++` code directly on a simulator.
