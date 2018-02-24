---
slug: cpp-for-mobile-part-4-android
date: 2018-02-24T17:18:19.722161+00:00
draft: true
title: "C++ for mobile part 4: Android"
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
