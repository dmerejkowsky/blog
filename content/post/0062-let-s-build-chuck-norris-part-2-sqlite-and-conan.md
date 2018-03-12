---
authors: [dmerej]
slug: chuck-norris-part-2-sqlite-conan
date: 2018-03-10T16:12:44.131649+01:00
draft: false
title: "Let's Build Chuck Norris! - Part 2: SQLite and conan"
tags: [c++]
---


# Adding dependency to sqlite3

* Get conan

* `conanfile.txt`

```cfg
[requires]
sqlite3/3.21.0@bincrafters/stable

[generators]
cmake
```

```console
$ cd build/desktop
$ conan install ..
```

```cmake

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

target_link_libraries(chucknorris
  PRIVATE
    CONAN_PKG::sqlite3
)
```

Notes:

* PRIVATE so that libchucknorris does not "really" depend on sqlite3
* use TARGETS (modern build system ftw)


```cpp
ChuckNorris::ChuckNorris()
{
  sqlite3_open(":memory:", &_db);

  auto const sql = R"(
CREATE TABLE chucknorris(id PRIMARY_KEY, fact VARCHAR(500));
INSERT INTO chucknorris (fact) VALUES
  ("Chuck Norris can slam a revolving door.");
INSERT INTO chucknorris (fact) VALUES
  ("Chuck Norris can kill two stones with one bird.");
  ...
  )";

  char* errorMessage = nullptr;
  auto res = sqlite3_exec(db, sql, 0, 0, &errorMessage);
}

std::string ChuckNorris::getFact()
{
  sqlite3_stmt* statement;
  int rc;
  rc = sqlite3_prepare_v2(_db,
      R"(SELECT fact FROM chucknorris ORDER BY RANDOM() LIMIT 1;)",
      -1, &statement, 0);

  rc = sqlite3_step(statement);
  auto sqlite_row = sqlite3_column_text(statement, 0);
  auto row = reinterpret_cast<const char*>(sqlite_row);
  return std::string(row);
}
```

Note: error handling omitted for brevity


# Note: recompile with -fPIC

Alas ...

```console
$ cmake -DBUILD_SHARED_LIBS=ON ../..
$ ninja
/bin/ld: .../libsqlite3.a(sqlite3.o): relocation R_X86_64_PC32
against symbol `sqlite3_version' can not be used when making
a shared object; recompile with -fPIC
```


* Fork uspstream recipe


```console
$ mkdir -p conan-recipes/sqlite3
$ cd conan-recipes/sqlite3
$ conan copy sqlite3/3.21.0@bincrafters/stable dmerej/test
$ cp -r ~/.conan/data/sqlite3/3.21.0/dmerej/test/export/ sqlite3
$ cp -r ~/.conan/data/sqlite3/3.21.0/dmerej/test/export_sources/* sqlite3
$ conan create . dmerej/test
```

* Patch `CMakeLists.txt` in `conan-recipes/sqlite3/CMakeLists.txt`:

```cmake
project(cmake_wrapper)
set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)

...
```

* Patch `conanfile.txt`
```cfg
[requires]
sqlite3/3.21.0@dmerej/test
```

Decentralized ftw !


PS: there's a reason to have `sqlite.a` *without* position independent code, ...
