---
authors: [dmerej]
slug: chuck-norris-part-8-android-jna
date: 2018-06-02T10:17:17.789657+00:00
draft: true
title: "Let's Build Chuck Norris! - Part 7: Android and jna"
tags: [c++]
---

_Note: This is part 7 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._


Let's take a detour on the desktop first.

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

But that's ok, we know how to cross-compile C++ code for Android, so all that's left to do is ...

# Symlinks


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
