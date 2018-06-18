---
authors: [dmerej]
slug: chuck-norris-part-8-android-jna
date: 2018-06-18T12:17:17.789657+00:00
draft: true
title: "Let's Build Chuck Norris! - Part 7: Android and jna"
tags: [c++]
---

_Note: This is part 7 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._


[Last time]({{< ref "post/0073-let-s-build-chuck-norris-part-6-android-cross-compilation.md" >}}) we managed to cross-compile and run C++ code for Android.

It's now time to write some Java code, but we need to take a detour on the desktop first.

# Java bindings


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

Then let's fix the source files that gradle created so that we have proper package:

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

Then we're ready to use JNA:

* We use `Native.loadLibrary()` to load the shared library
* We create a `CLibrary` interface that implements the C functions we want to call as methods. (just `chuck_norris_init` for now).
* We call `chuck_norris_init` in the constructor of our ChuckNorris class, storing the result into a jna `Pointer`:

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
  Native library (linux-x86-64/libchucknorris.so)
  not found in resource path (...)
  at com.sun.jna.NativeLibrary.loadLibrary(NativeLibrary.java:303)
  at com.sun.jna.NativeLibrary.getInstance(NativeLibrary.java:427)
  ...

```

This is expected. We never told jna where the `libchucknorris.so` file is.

As a reminder, the file currently lives in the `build/default` folder. Here's how we built it:

```
$ cd build/default
$ conan install ../..
$ cmake -GNinja -DBUILD_SHARED_LIBS=ON ../..
$ ninja
```

There are several ways to tell JNA about the location of the shared library file. Here we'll set a system property in the `test` block of the Gradle script:

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

Re-run the tests:

```
$ ./gradlew test
BUILD SUCCESSFUL
```

Success!

# Creating a new Android project

Now we know:

* How to compile the C++ code for Android.
* How to load some C++ in Java, but only for the desktop.

It's time to glue things together.

To do so, the best thing is to use Android Studio to create the gradle project, starting with a with a basic activity so we don't have to deal with all the Android boilerplate.

## Adapting the GUI


First let's pretend the ChuckNorris class already exists and

* Add a `text_view` ID for the text view in the `content_main` layout.
* Adapt the `MainActivity.java` file to  update the text view when clicking on the floating button action.


```java

public class MainActivity extends AppCompatActivity {
  private ChuckNorris chuckNorris;


  @Override
  protected void onCreate(Bundle savedInstanceState) {
    chuckNorris = new ChuckNorris();
    super.onCreate(savedInstanceState);
  }

  @Override
  protected void onDestroy() {
    chuckNorris.close();
    super.onDestroy();
  }

  // ...

  final TextView textView = (TextView) findViewById(R.id.text_view);
  FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
  fab.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View view) {
      String fact = chuckNorris.getFact();
      textView.setText(fact);
  });
```

## Adding ChuckNorris sources

One of Java's slogan is "Write Once, Run Everywhere" [^1].

So let's:

* Add jna in the dependencies
* Add the ChuckNorris.java file we wrote earlier

And everything should work, right?


## Fun with jnidispatch.so


To check if our code works, let's create an emulator, and click on play.

We're faced with:

> **ChuckNorris has stopped**
>
> Open App Again

What? Chuck Norris *can't be stopped*, this is unacceptable!

Time to look at the logs:

```
06-18 14:27:18.553 6890-6890/info.dmerej.chucknorris E/AndroidRuntime:
FATAL EXCEPTION: main
Process: info.dmerej.chucknorris, PID: 6890
java.lang.UnsatisfiedLinkError:
Native library (com/sun/jna/android-x86-64/libjnidispatch.so)
not found in resource path (.)
  at com.sun.jna.Native.loadNativeDispatchLibraryFromClasspath
  at com.sun.jna.Native.loadNativeDispatchLibrary
  ...
  at info.dmerej.chucknorris.ChuckNorris.loadChuckNorrisLibrary
```

That's a fun one. Turns out the name of dependency *changes* when compiling for Android, you need a `@aar` prefix [^2]:

```gradle
dependencies {
  // ...
  implementation 'net.java.dev.jna:jna:4.5.1@aar'
}
```

Let's try again!

We get the same error message, but this time it's the `chucknorris.so` library that is not found:

```
06-18 14:27:18.553 6890-6890/info.dmerej.chucknorris E/AndroidRuntime:
FATAL EXCEPTION: main
Process: info.dmerej.chucknorris, PID: 6890
java.lang.UnsatisfiedLinkError: Unable to load library 'chucknorris':
  Native library (android-x86-64/libchucknorris.so) not found
```

Fortunately, there's a more or less standard solution.

If you put a `.so` file in a folder named `src/main/jniLibs/<arch>`, it will be included inside the Java application, and the Java code will be able to load it without any configuration.


## The shared option


For simplicity purposes, we built the ChuckNorris library as a static library, just to show that the C++ binary still needed `libc++_shared.so` to run.
But JNA needs a shared library to run.


Remember in [part 4]({{< ref "post/0064-let-s-build-chuck-norris-part-4-python-and-ctypes.md" >}}) we had to call CMake with `-DBUILD_SHARED_LIBS=ON` to get a shared library.

We'll do the same thing, but going through Conan this time.

First, let's add the `ChuckNorris:shared` option in the `android` profile:

```ini
...
[options]
*:pic=True
ChuckNorris:shared=True
```

Then adapt the recipe:

{{< highlight python "hl_lines=4-5 9-12 15-16" >}}
class ChucknorrisConan(ConanFile):
    name = "ChuckNorris"
    ...
    options = {"shared": [True, False]}
    default_options = "shared=False"

    def build(self):
        cmake = CMake(self)
        cmake_definitions = {}
        if self.options.shared:
            cmake_definitions["BUILD_SHARED_LIBS"] = "ON"
        cmake.configure(defs=cmake_definitions)

    def package(self):
        self.copy("lib/libchucknorris.so", dst="lib", keep_path=False)
        self.copy("lib/libc++_shared.so", dst="lib", keep_path=False)
{{</ highlight >}}


Then let's re-create the Conan package:

```
$ conan create . dmerej/test --profile android --setting arch=x86_64
Exporting package recipe
...
package(): Copied 2 '.so' files: libchucknorris.so, libc++_shared.so
Package '<hash>' created
```

Finally let's create symlinks to all `.so` files from the package.

```
$ cd android/app
$ cd src/main
$ mkdir -p jniLibs/x86_64
$ cd jniLibs/x86_64
$ ln -s ~/.conan/data/ChuckNorris/0.1/dmerej/test/<hash>/libchucknorris.so .
$ ln -s ~/.conan/data/ChuckNorris/0.1/dmerej/test/<hash>/libc++_shared.so .
```

Let's try again:

![Chuck Norris app running](/pics/chuck-norris-android.png)

Victory \o/


That's all for today. See you next time!

[^1]: As always, the [Wikipedia page](https://en.wikipedia.org/wiki/Write_once,_run_anywhere) contains lots of interesting stuff about this topic.
[^2]: You can find a note about this in [JNA's FAQ](https://github.com/java-native-access/jna/blob/master/www/FrequentlyAskedQuestions.md#jna-on-android), but as far as I know, not *anywhere else* in the documentation.
