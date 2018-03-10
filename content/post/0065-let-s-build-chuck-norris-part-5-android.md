---
slug: chuck-norris-part-5-android
date: 2018-03-10T14:56:18.213047+01:00
draft: true
title: "Let's Build Chuck Norris! - Part 5: Android"
tags: [c++]
---

# Java

* Using jna

* Need to build a shared library (but still link with sqlite in static ...)

```console
$ mkdir -p cpp/build/java
$ cd cpp/build/java
$ conan install ../..
$ cmake -GNinja -DBUILD_SHAREDS_LIBS=ON ../..
$ ninja
```

```console
$ gradlew init --type java-library
```

```java
public class ChuckNorrisLib {
	private Pointer ckPointer;

    public interface CLibrary extends Library {
        CLibrary INSTANCE = (CLibrary)
            Native.loadLibrary("chucknorris", CLibrary.class);

        Pointer chuck_norris_init();
        String chuck_norris_get_fact(Pointer pointer);
        void chuck_norris_deinit(Pointer pointer);
    }

    public ChuckNorrisLib() {
        ckPointer = CLibrary.INSTANCE.chuck_norris_init();
    }

    public String getFact() {
        return CLibrary.INSTANCE.chuck_norris_get_fact(ckPointer);
    }

    // ...
}
```

```groovy
dependencies {
    api 'net.java.dev.jna:jna:4.5.1'
    testImplementation 'junit:junit:4.12'
}


def thisFile  = new File(project.file('build.gradle').absolutePath)
def projectPath = thisFile.getParentFile().getParentFile()
def cppBuildPath = new File(projectPath, "cpp/build/java/lib")

test {
    systemProperty 'jna.library.path', cppBuildPath
}
```


# Running tests

For some reason `jna.library.path` does not get set when running the tests from android studio.

"Solution":

* Create a new configuration to run all tests in package
* Add `-Djna.library.path=/path/to/build/java/lib` in the JVM options

    This works but you cannot run just one test from the IDE

Tip:
* For me Android studio no longer compiled the tests before running them, fixed it by
adding `compileTest` gradle task before launch.

# Android

Using the Android helper.

(Trust me on this)

## Tips

* Make sure to create a device with:

    * a x86_64 CUP (faster!)
    * lots of RAM and disk space (it's hidden in the "advanced" menu ..)


* If emulator does not start, use:

```console
$ cd ~/Android/Sdk/
$ ./tools/emulitors -list-avds
# to get your AVD name
$ ./tools/emulator -use-system-libs -avd <name>
```

# Add ChuckNorrisLib.java

Same as the `java` example.

Write once, run everywhere, they said :)

# Fun with jnidispatch.so


Let's try to make the tests in `src/test` work:

```java
public class ChuckNorrisTest {
    @Test
    public void testGetVersion() {
        String version = ChuckNorrisLib.getVersion();
        assertEquals(version, "0.1");
    }
}
```

Hu-ho:

```text
java.lang.UnsatisfiedLinkError:
Native library (com/sun/jna/android-x86-64/libjnidispatch.so)
not found in resource path (.)
```

Fortunately, there's a standard way to put `.so` files so that the get packaged inside and Android app, called the `jniLibs` folder.

You can find the `libjnidispatch.so` lib inside the `android-x86-84.jar` folder in the
[dist folder of jna on github](https://github.com/java-native-access/jna/tree/master/dist)


so that other devs can guess what to do, also add a `.gitignore` file:

```console
$ cat jniLibs/.gitignore
x86_64
# TODO: add more Android archs here
$  tree -a jniLibs
.
├── .gitignore
└── x86_64
    └── libjnidispatch.so
```

Note how the contents of the `.gitignore` also serves as a documentation as it lists the names of the Android archs :)

Note: there's probably a way to do that automatically with gradle, but life is short ...

Now the error becomes:

```console
java.lang.UnsatisfiedLinkError:
Unable to load library 'chucknorris':
Native library (android-x86-64/libchucknorris.so)
not found in resource path (.)
```

That means we now have to cross-compile our chucknorris lib for android x86-64

# Conan to the rescue

Follow [the fine documentation]http://docs.conan.io/en/latest/systems_cross_building/cross_building.html#linux-windows-macos-to-android)

Personally, I prefer to keep my conan profiles in `~/.conan/profiles/android-x86_64` so that I can omit
the full path when using `conan create`.

Let's cross-compile `sqlite3` for android:

```console
$ cd console-recipes/sqlite3
$ conan create . dmerej/test -p android-x86_64
```

And then cross-compile the `chucknorris` lib:

```console
$ cd cpp
$ mkdir build/android/x86_64
$ conan install ../../ -p android-x86_64
....
Cross-build from 'Linux:x86_64' to 'Android:x86_64'
sqlite3/3.21.0@dmerej/test: Already installed!
```

OK, now we are ready to build:


```console
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

```console
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

```console
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

```console
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


```console
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


# New symlinks

Now we can create a symlink to `cpp/build/android/x86_64/lib/libchucknorris.so` in
`android/app/src/main/jniLibs/x86_64/`

and a symlink to `/android-x86_64-api-27-toolchain/x86_64-linux-android/lib64/libc++_shared.so`

And the test pass!


# Finally, the GUI


Add a button and a text view.

Then patch the `MainActivity.java` class

```java
public class MainActivity extends AppCompatActivity {
    private ChuckNorrisLib cklib = new ChuckNorrisLib();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button button = findViewById(R.id.button);
        final TextView view = (TextView) findViewById(R.id.textView);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String fact = cklib.getFact();
                view.setText(fact);
            }
        });
    }
}

```


Done!
