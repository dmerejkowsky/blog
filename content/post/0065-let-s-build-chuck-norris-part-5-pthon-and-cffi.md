---
authors: [dmerej]
slug: chuck-norris-part-5-python-cffi
date: 2018-03-18T16:51:30.882200+00:00
draft: true
title: "Let's Build Chuck Norris! - Part 5: Python and cffi"
tags: [c++, python]
---

## First try with cffi



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
