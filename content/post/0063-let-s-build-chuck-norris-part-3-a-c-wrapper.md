---
authors: [dmerej]
slug: chuck-norris-part-3-a-c-wrapper
date: 2018-03-18T16:50:30.882200+00:00
draft: false
title: "Let's Build Chuck Norris! - Part 3: A C wrapper"
tags: [c++]
---

_Note: This is part 3 of the [Let's Build Chuck Norris!]({{< ref "0060-introducing-the-chuck-norris-project.md" >}}) series._

# Introduction: when languages talk together

C is kind like the lingua franca of programming languages. Many languages implementations are themselves *written* in C, and almost all of them know how to call C code. (Ofter this is called using a *Foreign Function Interface*, or FFI for short.

Our goal with the Chuck Norris project is to use our library in a lot of various situations (such as in an iOS or Android application), so why did we not write the chucknorris library in C?

Well, C++ has many advantages compared to C:

* Strings are easier to handle
* Memory management is simpler
* You can use nice tools such as classes and templates
* ... and more!

C and C++ are not so far apart: For instance, calling C from C++ works out of he box. `sqlite3` is written in C, and in our code we just had to include `<sqlite3.h>` and everything "just worked". [^1]

But things get more interesting when we try to go the other way around.

# Calling C++ code from C

In our library we expose a class, but C does not know about classes. So we are going to  declare a C API, and then implement the C API using C++ code.

We can do this because C++ is a "superset" of C.

There's a few details to get right though, so let's do this step by step.

## Declaring a C API


C does not know about classes, so we cannot use the `ChuckNorris` symbol anywhere.

Here's what we can do:

_include/chucknorris.h:_
```c
typedef struct chuck_norris chuck_norris_t;
chuck_norris_t* chuck_norris_init(void);
const char* chuck_norris_get_fact(chuck_norris_t*);
void chuck_norris_deinit(chuck_norris_t*);
```

* Each function is prefixed with `chuck_norris_` (because there are no namespaces in C)
* We declare a `chuck_norris_t` struct type but do not bother to describe what's inside. This works because the other functions will either return or take a parameter of the `chuck_norris_t` **pointer** type, so the compiler does not need to know what's inside the struct. This is known as an *opaque pointer*. In the C++ implementation, we'll have to perform casts between the "real" `ChuckNorris*` pointers and the opaque `chuck_norris*` ones.
* Instead of letting the compiler handle creation and destruction of the C++ class, we have explicit functions: `chuck_norris_init()` and `chuck_norris_deinit()`.
* Instead of a `getFact()` method inside a class, we have a `chuck_norris_get_fact()` function that takes opaque `chuck_norris` pointer as first parameter.


## Implementing the C API

Here's what our first attempt looks like:

_src/c_wrapper.cpp:_
```cpp
#include <chucknorris.hpp>

chuck_norris_t* chuck_norris_init()
{
  auto ck = new ChuckNorris();
  return reinterpret_cast<chuck_norris*>(ck);
}

const char* chuck_norris_get_fact(chuck_norris_t* chuck_norris)
{
  auto ck = reinterpret_cast<ChuckNorris*>(chuck_norris);
  std::string fact = ck->getFact();
  const char* result = fact.c_str();
  return result;
}

void chuck_norris_deinit(chuck_norris_t* chuck_norris)
{
  auto ck = reinterpret_cast<ChuckNorris*>(chuck_norris);
  delete ck;
}
```

The only cast we can use is `reinterpret_cast`, which basically tell the compiler "trust us, what's inside the pointer is of the right type!". This means things will go terribly wrong if callers of the C API are not careful, but don't worry, they're used to it :P

To check it works, let's add an other test executable, written in C this time:

_src/main.c_:
```c
#include <chucknorris.h>
#include <stdlib.h>
#include <stdio.h>

int main()
{
  chuck_norris_t* ck = chuck_norris_init();
  const char* fact = chuck_norris_get_fact(ck);
  printf("%s\n", fact);
  chuck_norris_deinit(ck);
  return 0;
}
```

Now let's adapt the CMake code to:

* Add the `c_wrapper.cpp` file to the list of the sources of the `chucknorris` library.
* Add a `c_demo` executable built with from the `main.c` file:

```patch
  add_library(chucknorris
    include/ChuckNorris.hpp
    include/chucknorris.h
    src/ChuckNorris.cpp
+   src/c_wrapper.cpp
  )

+ add_executable(c_demo
+   src/main.c
+ )
+
+ target_link_libraries(c_demo chucknorris)
```

And let's try to compile:

<pre>
$ cd build/default
$ ninja
[1/7] Building C object CMakeFiles/c_demo.dir/src/main.c.o
[2/7] Building CXX object CMakeFiles/chucknorris.dir/src/c_wrapper.cpp.o
[3/7] Building CXX object CMakeFiles/cpp_demo.dir/src/main.cpp.o
[4/7] Building CXX object CMakeFiles/chucknorris.dir/src/ChuckNorris.cpp.o
[5/7] Linking CXX static library lib/libchucknorris.a
[6/7] Linking CXX executable bin/c_demo
FAILED: bin/c_demo
: && /bin/c++ main.c.o -o bin/c_demo lib/libchucknorris.a ...
CMakeFiles/c_demo.dir/src/main.c.o: In function `main':
main.c:(.text+0x9): undefined reference to `chuck_norris_init'
main.c:(.text+0x19): undefined reference to `chuck_norris_get_fact'
main.c:(.text+0x35): undefined reference to `chuck_norris_deinit'
</pre>

We can see the `libchucknorris.a` library was passed to the linker, so why were the symbols not found ?

## Mangled symbols

To understand, let's look at the names of the symbols inside the `libchucknorris.a` library using a tool called `nm`:

<pre>
$ nm --defined-only libchucknorris.a

ChuckNorris.cpp.o:
0000000000000000 V DW.ref.__gxx_personality_v0
...
000000000000020c T _ZN11ChuckNorris7getFactB5cxx11Ev

c_wrapper.o
...
0000000000000000 T _Z17chuck_norris_initv
00000000000000ac T _Z19chuck_norris_deinitP11ChuckNorris
000000000000003c T _Z21chuck_norris_get_factP11ChuckNorris
</pre>

Hum. The names of the symbols do not match the ones we declared in the headers.

That's because they were *mangled* by the C++ compiler. I won't detail here the reasons why the symbols have to be mangled in the first place. Let's just say it has to do with stuff like function overloading and things like that.

We can check that the `cpp_demo` binary contains a reference to the weird `getFact` symbol:

<pre>
$ nm --defined-only cpp_demo
...
000000000000cefe T _ZN11ChuckNorris7getFactB5cxx11Ev
</pre>

We can also use the `--demangle` option when calling `nm` and see the original names:

(note that the C symbols were mangled too)

<pre>
$ nm --demangle --defined-only libchucknorris.a
...
00000000000001b0 T ChuckNorris::getFact[abi:cxx11]()
...
0000000000000000 T chuck_norris_init()
00000000000000ac T chuck_norris_deinit(ChuckNorris*)
000000000000003c T chuck_norris_get_fact(ChuckNorris*)

$ nm --demangle --defined-only cpp_demo
...
000000000000cefe T ChuckNorris::getFact[abi:cxx11]()
</pre>

When we compiled `c_demo.o`, we used a *C* compiler. (CMake saw a `.c` extension on the source files, and thus told ninja to build `main.c.o` with a C compiler)

Since the C compiler does *not* mangle symbols at all, the final link between `c_demo.o` and `libchucknorris.a` failed.

The solution is to tell the C++ compiler to *not* mangle the symbols defined in the `chucknorris.h` header using the `extern` syntax

```cpp

extern "C" {

  chuck_norris_t* chuck_norris_init(void);
  char* chuck_norris_get_fact(chuck_norris_t*);
  void chuck_norris_deinit(chuck_norris_t*);

}
```

But if we do that, we now get a compile failure because the C compiler does not understand the `extern` syntax:

<pre>
$ ninja
/bin/cc  -o main.c.o -c main.c
In file included from ../../src/main.c:1:0:
chucknorris.h:3:8: error: expected identifier or ‘(’ before string constant
extern "C" {
</pre>


Fortunately, the C++ compiler sets a `__cplusplus` define for us:

```cpp

#ifdef __cplusplus
extern "C" {
#endif

  chuck_norris_t* chuck_norris_init(void);
  const char* chuck_norris_get_fact(chuck_norris_t*);
  void chuck_norris_deinit(chuck_norris_t*);

#ifdef __cplusplus
}
#endif
```

Now the build passes [^2], and we can double-check the names of symbols inside the archive:

<pre>
$ ninja
[1/7] Building C object CMakeFiles/c_demo.dir/src/main.c.o
[2/7] Building CXX object CMakeFiles/chucknorris.dir/src/c_wrapper.cpp.o
[3/7] Building CXX object CMakeFiles/cpp_demo.dir/src/main.cpp.o
[4/7] Building CXX object CMakeFiles/chucknorris.dir/src/ChuckNorris.cpp.o
[5/7] Linking CXX static library lib/libchucknorris.a
[6/7] Linking CXX executable bin/cpp_demo
[7/7] Linking CXX executable bin/c_demo

$ nm --defined-only libchucknorris.a
ChuckNorris.cpp.o:
0000000000000000 V DW.ref.__gxx_personality_v0
...
0000000000000160 T _ZN11ChuckNorrisC1Ev
...
000000000000020c T _ZN11ChuckNorris7getFactB5cxx11Ev

c_wrapper.o
...
0000000000000000 T chuck_norris_init
00000000000000ac T chuck_norris_deinit
000000000000003c T chuck_norris_get_fact
</pre>

## The string bug

Hooray, we managed to build our C code! Let's run it:

<pre>
$ ./bin/c_demo
���rU
 ./bin/c_demo
����BV
./bin/c_demo
`15R�U
</pre>

Hum. Something is not right.

Let's take a look again at the `chuck_norris_get_fact` implementation:

```cpp
const char* chuck_norris_get_fact(chuck_norris_t* chuck_norris)
{
  std::string fact = chuck_norris->getFact();
  const char* result = fact.c_str();
  return result;
}
```

Here's what's happening:

* First we call `chuck_norris->getFact()` and create a local variable named `fact`
* Then we get a `char*` pointer to the contents of the `std::string` with `c_str()`
* We return the `char*` pointer
* But then the `fact` variable gets out of scope and the contents of the `std::string` are freed. Note that this is what `std::string`s are *designed* to do: they handle memory management for us. We are only having this problem because we are playing with raw C pointers!
* Now our `char*` pointer points to uninitialized stuff and we get garbage.

The solution is to call `strdup` to get a copy of the contents that we now *own* and to free it explicitly later on.

(Note that the returned pointer is no longer `const`.)


_src/c_wrapper.cpp:_
```cpp
char* chuck_norris_get_fact(chuck_norris_t* chuck_norris)
{
  std::string fact = chuck_norris->getFact();
  char* result = strdup(fact.c_str());
  return result;
}
```

_src/main.c:_
```c
int main()
{
  chuck_norris_t* ck = chuck_norris_init();
  char* fact = chuck_norris_get_fact(ck);
  printf("%s\n", fact);
  free(fact);
  chuck_norris_deinit(ck);
  return 0;
}
```

And now the binary works:

<pre>
$ ninja
$ ./bin/c_demo
Chuck Norris doesn't dial the wrong number.
You answered the wrong phone.
</pre>

That's all for today. The C library is the building block we'll use to write Python bindings and phone applications. Stay tuned for the rest of the story!


[^1]: That's a lie. There's something special in the `sqlite3.h` file to make this work. But we'll talk about that later.
[^2]: This little trick of `#ifdef __cplusplus` and `extern "C"` is used pretty often in the wild, and you do find it in the `sqlite3.h` header. I had to lie to preserve the flow of the article, sorry.
