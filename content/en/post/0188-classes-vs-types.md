---
authors: [dmerej]
slug: classes-vs-types
date: 2022-06-23T10:11:47.416699+00:00
draft: true
title: "No, not classes. Types!"
tags: [rust]
summary: A follow-up to the "do classes suck or rock?" debate
---

# Introduction

Note: this is both a follow-up to the [do classes suck]({{< relref "0107-classes-suck.md" >}}) or [do classes suck]({{< relref "0108-classes-rock.md" >}}) articles, *and*
yet another reason why you should [learn Rust]({{< relref "./0117-rust-secrets-and-logs.md" >}}).

![](/pics/classes-vs-types.png)

# Back to the spec

As a reminder, here's our spec:

* When robots come off the factory floor, they have no name.

* The first time you boot them up, a random name is generated.

* Every once in a while, the robot are reset to their factory settings, and the next time you ask, they will respond with a new random name.

# Using Rust

Something about expressivens, correctness and performance.

What's interesting with the Rust programming language is that we can express the spec in such a way that **invalid states lead to compilation errors** and **without using anything but structs and methods**.

Here's how. We're going to use 2 types - and to be precise, those are called *structs*:

```rust
// We wrap the robot name (a *owned* string)
// inside a struct
pub struct NamedRobot {
  name: String,
}

// We create a brand new types for "robots that don't have names" yet
pub struct UnnamedRobot;

// Interestingly, this struct costs *nothing* to allocate and is known
// us a zero-sized type (ZST) in Rust parlance.
```

Then we can express the *transitions* behing allowed stateds as public methods on
those types (inside a `impl` block) or as free functions

Note: that most of the bodies are omitted here, but you can find
tho whole source code [on github](https://github.com/dmerejkowsky/robots/blob/master/rust/src/lib.rs)

```rust
// Note: this is a private implementation detail, so no
// `pub` here!
fn generate_random_name() -> String { /* ... */ }

pub fn new_robot() -> UnnamedRobot { /* ... */ }

impl UnnamedRobot {
    pub fn start(self) -> NamedRobot {
      let name = generate_random_name();
      NamedRobot { name }
    }
}

impl NamedRobot {
    pub fn name(&self) -> &str { /* ... */ }

    pub fn stop(&self) { /* ... */ }

    pub fn start(&self) { /* ... */ }

    // Note: taking ownership of `self` here!
    pub fn reset(self) -> UnnamedRobot { /* ... */ }
}
```

That way, invalid code won't compile. For instance:

```rust
let robot = new_robot();
let name = robot.name()
// Error: method name() not found for UnnamedRobot
```

You can reset a robot, restart it and get a new name:


```rust
let robot = new_robot();
let robot = robot.start();
let name1 = robot.name().to_string();

let robot = robot.reset();

let robot = robot.start();
let name2 = robot.name().to_string();
assert_ne!(name1, name2);
```

# Owning and borrowing

But what if you try to get a robot name *after* it has been reset?

```rust
let robot = new_robot();
let robot = robot.start();
let name1 = robot.name().to_string();
robot.reset();
let name2 = robot.name();
```

Well, you get an error from the *borrow checker*:

```
// Error: value `robot`  moved during called to reset reset()
```


