---
authors: [dmerej]
slug: chuck-norris-part-3-a-c-wrapper
date: 2018-03-18T16:50:30.882200+00:00
draft: true
title: "Let's Build Chuck Norris! - Part 3: A C wrapper"
tags: [c++]
---

# Opaque pointer

```c
#ifdef __cplusplus
extern "C" {
#endif

typedef struct ChuckNorris chuck_norris_t;
chuck_norris_t* chuck_norris_init(void);
const char* chuck_norris_get_fact(chuck_norris_t*);
void chuck_norris_deinit(chuck_norris_t*);

#ifdef __cplusplus
}
#endif
```

* `ifdef __cplusplus + extern "C"`: so that the symbols have the same name in C and C++
  TODO: talk about mangling and c++filt here


* We are the only one to know that ChuckNorris is actually a class. Consumer of `chuck_norris.h` only see a pointer to a un-defined struct.


# C++ implem

```cpp
#include <chucknorris.hpp>

chuck_norris_t* chuck_norris_init()
{
  return new ChuckNorris();
}

const char* chuck_norris_get_fact(chuck_norris_t* chuck_norris)
{
  return strdup(chuck_norris->getFact().c_str());
}

void chuck_norris_deinit(chuck_norris_t* chuck_norris)
{
  delete chuck_norris;
}
```

* `include <chucknorris.hpp` <- that's the secret !

* `strdup` because the address of the contents returned by `.c_str()` are
  in a temporary variable


* using `init`, `deinit` because ChuckNorris can't really be destroyed ...


# Testing it works


```cmake
add_executable(c_demo
  src/main.c
)

target_link_libraries(c_demo chucknorris)
```

```c

int main()
{
  chuck_norris_t* ck = chuck_norris_init(ck);
  const char* fact = chuck_norris_get_fact(ck);
  printf("%s\n", fact);
  chuck_norris_deinit(ck);
  return 0;
}
```


# Digression: writing a Python binding


## First try with cffi


For now, `chucknorris` lib is a `.a`. We could have made a `.dylib` by using `cmake -DBUILD_SHARED_LIBS=ON`.


```python
ffibuilder.set_source(
    "_chucknorris",
    """
    #include <chucknorris.h>

    """,
    extra_objects=[
        "../cpp/build/default/lib/libchucknorris.a",
    ],
    include_dirs=["../cpp/include"],
)

ffibuilder.cdef("""
typedef struct ChuckNorris chuck_norris_t;
chuck_norris_t* chuck_norris_init(void);
const char* chuck_norris_get_fact(chuck_norris_t*);
void chuck_norris_deinit(chuck_norris_t*);
""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
```

```python
from _chucknorris import lib, ffi

chuck_norris = lib.chuck_norris_init()
fact = lib.chuck_norris_get_fact(chuck_norris)
as_bytes = ffi.string(fact)
print(as_bytes.decode(), end="")
```

Small `cffi` gripe: `cffi.string()` could have a `cffi.bytes()` alias in Python3 ...


## The missing symbol

```console
$ python3 setup.py clean develop
running clean
removing 'build/temp.macosx-10.13-x86_64-3.6' (and everything under it)
running develop
...
running build_ext
generating cffi module 'build/temp.macosx-10.13-x86_64-3.6/_chucknorris.c'
creating build/temp.macosx-10.13-x86_64-3.6
building '_chucknorris' extension
...
clang
  -I/Python.framework/Versions/3.6/include/python3.6m
  -I../cpp/include
  ...
  -c build/temp.macosx-10.13-x86_64-3.6/_chucknorris.c
  -o build/temp.macosx-10.13-x86_64-3.6/_chucknorris.o
clang
  -bundle
  build/temp.macosx-10.13-x86_64-3.6/_chucknorris.o
  ../cpp/build/default/lib/libchucknorris.a
  -o build/lib.macosx-10.13-x86_64-3.6/_chucknorris.abi3.so
copying build/lib.macosx-10.13-x86_64-3.6/_chucknorris.abi3.so ->
```

Worth to notice:

* `clean develop` actually runs `clean, build_ext, develop`
* `-I../cpp/include` and `../cpp/build/default/lib/libchucknorris.a` come from our additions
  in `build_chucknorris.py`
* `develop` **copies** the `.so` at the root of the source folder. (be careful when you rebuild the extension!)

Let's try:

```console
$ python3 chucknorris.py
Traceback (most recent call last):
  File "chucknorris.py", line 1, in <module>
    from _chucknorris import lib, ffi
ImportError: dlopen(_chucknorris.abi3.so):
  Symbol not found: _sqlite3_close
```

On linux:

```
_ZTVN10__cxxabiv117__class_type_infoE
```

Fixed by adding `stdc++` to the list of libs:

```python
additional_libs = list()
if sys.platform == "linux":
    additional_libs.append("stdc++")


ffibuilder.set_source(
    "_chucknorris",
    """
    #include <chucknorris.h>

    """,
    extra_objects=libs,
    libraries=additional_libs,
    include_dirs=["../cpp/include"],
)
```


# Asking conan for the .a path

* [Add a json generator](https://github.com/conan-io/conan/pull/2515)

* Then parse it in the `build_chucknorris.py` file:

```python
cpp_build_path = path.Path("../cpp/build/default").abspath()
libs = []

libchucknorris_path = cpp_build_path.joinpath("lib/libchucknorris.a")
libs.append(libchucknorris_path)

conan_info = json.loads(cpp_build_path.joinpath("conaninfo.json").text())
for dep in conan_info["dependencies"]:
    for lib_name in dep["libs"]:
        lib_filename = "lib%s.a" % lib_name
        for lib_path in dep["lib_paths"]:
            candidate = path.Path(lib_path).joinpath(lib_filename)
            if candidate.exists():
                libs.append(candidate)


ffibuilder.set_source(
    "_chucknorris",
    ...
    extra_objects=libs,
    ...
)
```
