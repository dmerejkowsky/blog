---
authors: [dmerej]
slug: classes-suck-rock
date: 2022-06-18T10:11:47.416699+00:00
draft: false
title: "No, not classes. Types!"
tags: [rust]
summary: A follow-up to the "do classes suck or rock?" debate
---

# Introduction

Note: this is both a follow-up to the do classes [rock] or [suck] articles, *and*
yet another reason why you should [learn Rust]().

# Same thing, in Rust

As a reminder, here's our spec:

* When robots come off the factory floor, they have no name.

* The first time you boot them up, a random name is generated.

* Every once in a while, the robot are reset to their factory settings, and the next time you ask, they will respond with a new random name.

What's interesting here is that we can express the spec in such a way that **invalid states lead to compilation errors**.

Here's how. We're going to use 2 types:

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
those types or as free functions (bodies of which are omitted here for brevity)

```rust
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

    // Note: taking ownership of `self` here, meaning the struct is no longer
    // available after this method is called.
    pub fn reset(self) -> UnnamedRobot { /* ... */ }
}
```

That way, invalid code won't compile. For instance:

```rust
let robot = new_robot();
let name = robot.name() 
// Error: method name() not found for UnnamedRobot
```

Or, due to the `reset()`  method taking ownership of `self`:

```rust
let robot = new_robot();
let robot = robot.start();
let name1 = robot.name().to_string();
robot.reset();
let name2 = robot.name(); 
// Error: value `robot`  moved during called to reset reset() line 84
```

And of course, you can reset a robot, restart it and get a new name:

```rust
let robot = new_robot();
let robot = robot.start();
let name1 = robot.name().to_string();

let robot = robot.reset();

let robot = robot.start();
let name2 = robot.name().to_string();
assert_ne!(name1, name2);
```
