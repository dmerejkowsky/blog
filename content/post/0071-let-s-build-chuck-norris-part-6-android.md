---
authors: [dmerej]
slug: chuck-norris-part-6-android
date: 2018-06-02T10:17:17.789657+00:00
draft: false
title: "Let's Build Chuck Norris! - Part 6: Android"
tags: [c++]
---

_Note: This is part 6 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._

We now know how to wrap the ChuckNorris C++ library in Python.

For Android, we'll need to:

* Wrap the C++ library in Java (this is quite similar to what we did with Python and ctypes)
* Cross-compile the C++ library for Android (that's a big one ...)

Let's start with the Java bindings.

# Java bindings

As a reminder, the `build/default` folder already contains our shared library, here's how we built it:

```
$ cd build/default
$ conan install ../..
$ cmake -GNinja -DBUILD_SHARED_LIBS=ON ../..
$ ninja
```

Let's create a new Java library project with `gradle`:


```
$ cd chucknorris
$ mkdir java && cd java
$ gradle init --type java-library
```

Gradle created a bunch of files, but for now we just care about the sources and the tests.

Our goal is to write a test that demonstrates we can indeed get some ChuckNorris facts.

Let's start by removing cruft from the generated `build.gradle`:

```diff
dependencies {
-    api 'org.apache.commons:commons-math3:3.6.1'
-    implementation 'com.google.guava:guava:23.0'
}
```

Let's rename the source files that gradle created into a proper package and with a correct name to have:

```
$ tree java
├── build.gradle
├── gradle
└── src
    ├── main
    │   └── java
    │       └── com
    │           └── chucknorris
    │               └── ChuckNorris.java
    └── test
        └── java
            └── com
                └── chucknorris
                    └── ChuckNorrisTest.java
```

Now we can write a failing test:



```java
/* In ChuckNorrisTest.java */
public class ChuckNorrisTest {

    @Test
    public void testGetFact() {
        ChuckNorris ck = new ChuckNorris();
        String fact = ck.getFact();
        assertThat(fact, containsString("Chuck Norris"));
    }
}
```


```java
/* In ChuckNorris.java */

public class ChuckNorris {
    String getFact() {
        return "";
    }
}
```

Let's run the tests:

```
$ ./gradelew test
> Task :test FAILED

com.chucknorris.ChuckNorrisTest > testGetFact FAILED
    java.lang.AssertionError at ChuckNorrisTest.java:14

1 test completed, 1 failed

# open build/reports/tests/test/index.html

java.lang.AssertionError:
Expected: a string containing "Chuck Norris"
     but: was ""
```

OK, this fails for the good reason.

Now we can try and load our shared library using jna.

First, we add the dependency in the `build.gradle` file:

```diff
dependencies {
+   api 'net.java.dev.jna:jna:4.5.1'
    testImplementation 'junit:junit:4.12'
}
```

Then, we add the following code into the `ChuckNorris.java` class and use the `loadLibrary` method
from jna's `Native` class.

We also call `chuck_norris_init` in the constructor, storing the result into a jna `Pointer`:

```java
public class ChuckNorris {
  private Pointer ckPointer;

  private static CLibrary loadChuckNorrisLibrary() {
    return (CLibrary) Native.loadLibrary("chucknorris", CLibrary.class);
  }

  public interface CLibrary extends Library {
    CLibrary INSTANCE = loadChuckNorrisLibrary();

    void chuck_norris_init();
  }

  public ChuckNorris() {
    ckPointer = CLibrary.INSTANCE.chuck_norris_init();
  }

  public String getFact() {
    return "";
  }
}
```

And we run the tests:

```
$ ./gradlew test
java.lang.UnsatisfiedLinkError: Unable to load library 'chucknorris':
Native library (linux-x86-64/libchucknorris.so) not found in resource path (...)
	at com.sun.jna.NativeLibrary.loadLibrary(NativeLibrary.java:303)
	at com.sun.jna.NativeLibrary.getInstance(NativeLibrary.java:427)
        ...

```

This is expected. We never told jna where the `libchucknorris.so` file lived.

There are several ways to do this. Here we'll set a system property in the `test` block of the Gradle configuration file:

```gradle
def thisFile  = new File(project.file('build.gradle').absolutePath)
def projectPath = thisFile.getParentFile()
def topPath = projectPath.getParentFile()
def cppPath = new File(topPath, "cpp")
def cppBuildPath = new File(cppPath, "build/default/lib")

test {
    systemProperty 'jna.library.path', cppBuildPath
}
```

Now if we re-run the tests we get back our first failure:

```
$ ./gradlew test

java.lang.AssertionError:
Expected: a string containing "Chuck Norris"
     but: was ""
```

But we did manage to instantiate the `ChuckNorris` class, so this is progress :)

Let's implement `getFact()`, and while we're at it, add a `.close()` method:


```java

  public interface CLibrary extends Library {
    // ...
    void chuck_norris_init();
    String chuck_norris_get_fact(Pointer pointer);
    void chuck_norris_deinit(Pointer pointer);
  }

  public ChuckNorris() {
    ckPointer = CLibrary.INSTANCE.chuck_norris_init();
  }

  public String getFact() {
    return CLibrary.INSTANCE.chuck_norris_get_fact(ckPointer);
  }

  public void close() {
    CLibrary.INSTANCE.chuck_norris_deinit(ckPointer);
  }
}
```

```
$ ./gradlew test
BUILD SUCCESSFUL
```

Success!


# Android

Using the Android helper.

(Trust me on this)

## Tips

* Make sure to create a device with:

    * a x86_64 CUP (faster!)
    * lots of RAM and disk space (it's hidden in the "advanced" menu ..)


* If emulator does not start, use:

```
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

```
java.lang.UnsatisfiedLinkError:
Native library (com/sun/jna/android-x86-64/libjnidispatch.so)
not found in resource path (.)
```

Fortunately, there's a standard way to put `.so` files so that the get packaged inside and Android app, called the `jniLibs` folder.

You can find the `libjnidispatch.so` lib inside the `android-x86-84.jar` folder in the
[dist folder of jna on github](https://github.com/java-native-access/jna/tree/master/dist)


so that other devs can guess what to do, also add a `.gitignore` file:

```
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

```
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

```
$ cd console-recipes/sqlite3
$ conan create . dmerej/test -p android-x86_64
```

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
