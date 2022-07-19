---
authors: [dmerej]
slug: classes-vs-types
date: 2022-06-23T10:11:47.416699+00:00
draft: true
title: "Classes vs Types (or Yet Another Reason To Learn Rust)"
tags: [rust]
summary: A follow-up to the "do classes suck or rock?" debate
---

# Introduction

Note: this is both a follow-up to the [do classes suck]({{< relref "0107-classes-suck.md" >}}) or [do classes suck]({{< relref "0108-classes-rock.md" >}}) articles, *and*
yet another reason why you should [learn Rust]({{< relref "./0117-rust-secrets-and-logs.md" >}}), so you should have read at least one of them in order to understand the context for this post.

![](/pics/classes-vs-types.png)

# Back to the spec

As a reminder, here's our spec:

* When robots come off the factory floor, they have no name.

* The first time a robot boots, a random name is generated.

* Every once in a while, the robots are reset to their factory settings, and the next time they boot, they get a *new* random name.

# Using Rust

The goal of Rust is to allow to code to be 3 things at once: correct, fast, and expressive. This is no easy task and that's why Rust is a bit complicated to learn (which is not such a bad thing in my opinion, but I digress).

Anyway, what's interesting with the Rust programming language is that we can express the spec in such a way that **invalid states lead to compilation errors** and **without using anything but structs and methods**.

Here's how. Since the specs talks about names that may or may not exist, we're going to use two different types - one for the unnamed robots, and one for the robots that have a name. To be precise, those are called *structs*:

```rust
// We wrap the robot name  inside a struct
pub struct NamedRobot {
  name: String,
}

// We create a brand new type for "robots that don't have names" yet
pub struct UnnamedRobot;

// Note : interestingly, this struct costs *nothing* to allocate and is
// known as a zero-sized type (ZST) in Rust parlance.
```

Then we can express the *transitions* between allowed states as public methods on those types (inside a `impl` block) or as free functions

Note: that most of the bodies are omitted here, but you can find tho whole source code [on github](https://github.com/dmerejkowsky/robots/blob/main/rust/src/lib.rs)

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

Valid code does compile of course

```rust
let robot = new_robot();
let robot = robot.start();
let name = robot.name();
println!("New robot with name: {name}");
```

And invalid code won't compile. For instance:

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

You may wondering why we need `.to_string()` here. Well, let me explain.

# Owning and borrowing

I mentioned earlier that `reset` *takes ownership* of the robot.

That's because the method uses `self` as first parameter.

In contrast, the `name` method uses `&self` and *borrows* the robot.

This matters because in addition to having a rich type system as we saw above,
the Rust compiler also enforce rules about ownership.

Here are those rules:
* Each value in Rust has an owner.
* There can only be one owner at a time.
* At any given time, you can have either **one mutable** reference or any
  number of **immutable** references.

What this means is that when the robot is started, you can access the robot name any time
you want, as long as you don't try to modify it. *But*, once `reset()` is called, the value
has been moved, and thus you can no longer access the robot name.

Let's this in practice:

```rust
let robot = new_robot();
let robot = robot.start();
let name1 = robot.name().to_string();
let name2 = robot.name().to_string();
robot.reset();
let name3 = robot.name();
```

```
// Error: value `robot`  moved during called to reset reset()
```

If Rust had allowed this code to compile, we would have a `name3` variable *after*
the robot has been reset, which is not allowed by our spec!

Note that this also means we can't have `name1` and `name2` be merely string references (`&str`).

That's why we use the `.to_string()` method, which gives us as a *mutable copy* (a `String`) for the robot name.


## Conclusion

If you learn Rust, you'll find that:

* There's more to Object-Oriented Programming than just classes
* The borrow checker, when used well, can prevent a bunch of mistakes **at compile time**.

Side note: I used two different types to make a point. You will find a more idiomatic version of the code in the [aptly named "idiomatic" branch on GitHub](
https://github.com/dmerejkowsky/robots/blob/idiomatic/rust/src/lib.rs).

The again show again how the borrow checker rules prevent invalid states *at compile time*, this time because some methods (like `start` or `reset`) use `&mut self` and other just `&self` (like `name`). It also shows the "new type" pattern, in order to enforce robot name format at runtime.
