---
authors: [dmerej]
slug: rusty-chuck
date: 2019-09-08T12:54:35.332456+00:00
draft: true
title: "Rusty Chuck"
tags: [rust]
summary: "Let's Rewrite ChuckNorris in Rust!"
---

# Rust implem

```
cargo new --lib chucknorris
```

```toml
[dependencies]
toml = "*"
rand = "*"
```


```rust
use rand;
use rand::rngs::ThreadRng;
use rand::Rng;
use toml;

pub struct ChuckNorris {
    facts: Vec<toml::Value>,
    rng: ThreadRng,
}

impl ChuckNorris {
    pub fn new() -> Self {
        let contents = include_str!("facts.toml");
        let parsed = contents
            .parse::<toml::Value>()
            .expect("could not parse facts.toml");
        let facts = parsed["facts"]
            .as_array()
            .expect("no 'facts' key as array in facts.toml");
        let rng = rand::thread_rng();
        ChuckNorris {
            facts: facts.to_vec(),
            rng,
        }
    }

    pub fn version() -> &'static str {
        "0.1"
    }

    // TODO: can we avoid get_fact() being mut?
    pub fn get_fact(&mut self) -> String {
        let num_facts = self.facts.len();
        let index = self.rng.gen_range(0, num_facts);
        let fact = self.facts[index].as_str().expect("key is not a string");
        fact.to_string()
    }
}
```

# Writing C bindings


```
#[no_mangle]
pub extern "C" fn chuck_norris_version() -> *mut c_char {
    let version = ChuckNorris::version();
    let c_str = CString::new(version).expect("could not convert to C string");
    c_str.into_raw()
}

#[no_mangle]
pub extern "C" fn chuck_norris_init() -> *mut ChuckNorris {
    let ck = unsafe { transmute(Box::new(ChuckNorris::new())) };
    ck
}

#[no_mangle]
pub extern "C" fn chuck_norris_deinit(ptr: *mut ChuckNorris) {
    let ck: Box<ChuckNorris> = unsafe { transmute(ptr) };
    drop(ck);
}

#[no_mangle]
pub extern "C" fn chuck_norris_get_fact(ptr: *mut ChuckNorris) -> *mut c_char {
    let ck = unsafe { &mut *ptr };
    let fact = ck.get_fact();
    let c_str = CString::new(fact).expect("Could not convert to C string");
    c_str.into_raw()
}
```

Note: *very* similar to the C++ stuff, expect we cannot return a pointer to a local variable anymore, and that
the pointer is no longer const ...

# cbindgen

```toml
[build-dependencies]
cbindgen = "0.6.3"


[lib]
name = "chucknorris"
crate-type = ["staticlib"]
```


```toml
# cbindgen.toml
language="c"
```

```rust
// build.rs
extern crate cbindgen;

use std::env;

fn main() {
    let crate_dir = env::var("CARGO_MANIFEST_DIR").expect("CARGO_MANIFEST_DIR not set");

    cbindgen::generate(crate_dir)
        .expect("Unable to generate bindings")
        .write_to_file("target/c/chucknorris.h");
}
```

```
cargo build
```

Let's take a look

```c
// in target/c/

#include <stdarg.h>
// ...

typedef struct ChuckNorris ChuckNorris;

void chuck_norris_deinit(ChuckNorris *ptr);
char *chuck_norris_get_fact(ChuckNorris *ptr);
ChuckNorris *chuck_norris_init(void);
char *chuck_norris_version(void);
```

Note how cbindgen just had to parse the `pub` declarations and the rust docstrings :)

# Python

No need for parsing json stuff, we just need:

```python
 ffibuilder.set_source(
     "_chucknorris",
     """
     #include <chucknorris.h>
     """,
    include_dirs = ["../rust/target/c/"],
    extra_objects=["../rust/target/debug/libchucknorris.a"],
```

# Java

We need a `.so` for JNA:

```toml
[lib]
name = "chucknorris"
crate-type = ["staticlib", "dylib"]
```

That way `cargo build` builds both the `.a` and the `.so` :)

# Android

* We can do it in two commands:

```
rustup target add x86_64-linux-androideabi
cargo build --target x86_64-linux-androideabi
```

* We don't need to worry about libstdc++

