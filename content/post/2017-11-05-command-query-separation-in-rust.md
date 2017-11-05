---
slug: command-query-separation-in-rust
date: 2017-11-05T13:02:15.483612+00:00
draft: true
title: Command Query Separation in Rust
tags: ["rust"]
---

# Introduction

This week-end I read the [Rust Programming Language](https://doc.rust-lang.org/book/second-edition/) book.

I've a ton of stuff to say about `rust` but for now, I'd like to talk about a certain compile failure I've got, how I solved it, and why you should care.

# Expressing a process with types

Let's say you are implementing a service where people can post blog posts.

We have two requirements:
* Posts must be reviewed before they can be published
* Once the review has started, the text cannot change. (You'll have to submit a new version)

Here's what the production code looks like:


```rust
fn main() {
use  blog::Post;

fn publish(post: &Post) {
    println!("Publishing post: {}", post.content());
}


fn main() {
    let mut post = Post::new();
    post.add_text("I ate a salad for lunch today");
    let post = post.request_review();
    let post = post.approve();
    publish(&post);
}
```

And here's the implementation:


```rust
pub struct Post {
    content: String,
}

pub struct DraftPost {
    content: String,
}

impl DraftPost {
    pub fn add_text(&mut self, text: &str) {
        self.content.push_str(text);


    pub fn request_review(self) -> PendingReviewPost {
        PendingReviewPost {
            content: self.content,
        }
    }

}

pub struct PendingReviewPost {
    content: String,
}

impl PendingReviewPost {
    pub fn approve(self) -> Post {
        Post {
            content: self.content
        }
    }
}


impl Post {
    pub fn new() -> DraftPost {
        DraftPost {
            content: String::new(),
        }
    }


    pub fn content(&self) -> &str {
        &self.content
    }
}
```


Each state of the publishing process is expressed in a different type:

* We start we `Post::new()`, which returns a `DraftPost`
* Then we can call `request_review` on `DraftPost` and get a `PendingReviewPost`
* Then we call `approve` on `PendingReviewPost` and get back a `Post`
* Finally, we call the `content()` getter

This way we can't write something like:

```rust
    let mut post = Post::new();
    post.add_text("I ate a salad for lunch today");
    let post = post.request_review();
    // let post = post.approve();
    publish(&post);
```

The compiler will tell us:

```text
error[E0308]: mismatched types
  --> src/main.rs:14:13
   ...
   = note: expected type `&blog::Post`
              found type `&blog::PendingReviewPost`
```

We also use a very specify feature of rust: all the function take `self`, which means they take ownership when they are called.
Which means that after call `post.request_review()`, you *cannot* call `add_text()` anymore because the variable has "moved":

```rust
let mut post = Post::new();
post.add_text("I ate a salad for lunch today");
let pending_post = post.request_review();
post.add_text("Changed my mind");
```

```text
error[E0382]: use of moved value: `post`
  --> src/main.rs:13:5
   |
12 |     let pending_post = post.request_review();
   |                        ---- value moved here
13 |     post.add_text("Changed my mind");
   |     ^^^^ value used here after move
```

What happened is that all the contents of the `Post` struct have moved into the `pending_post` variable, so it's no longer available after the call to `request_review()`.

You can, however, create a new post instance:

```rust
let mut post = Post::new();
post.add_text("I ate a salad for lunch today");
let pending_post = post.request_review();
let mut post2 = Post::new();
post2.add_text("Changed my mind");
post2.request_review();
```

# A new requirement

But then on new requirements comes up. We need *two* approvals before authorizing the publication.

I figured I could just patch the code so that:

* `PendingReviewPost` would contain a `approvals` count
* `DraftPost.request_review()` would crate a `PendingReviewPost` with 0 approvals
* `PendingReviewPost.approve()` would
`approve()` function to:


return an `Option` instead:

```rust

impl DraftPost {
    // ...

    pub fn request_review(self) -> PendingReviewPost {
        PendingReviewPost {
            content: self.content,
            approvals: 0,
        }
    }
}
pub struct PendingReviewPost {
    content: String,
    approvals: u64,
}

impl PendingReviewPost {
    pub fn approve(self) -> Option<Post> {
        self.approvals += 1;
        if self.approvals < 2 {
            None
        } else {
            Some(Post{content: self.content})
        }
    }
}
```

As expected, the compiler complained I was mutating the `PendingReviewPost` in the `approve` function:

```text
error[E0594]: cannot assign to immutable field `self.approvals`
  --> src/lib.rs:30:9
   |
29 |     pub fn approve(self) -> Option<Post> {
   |                    ---- consider changing this to `mut self`
30 |         self.approvals += 1;
   |
```

So I went ahead and changed `self` to `&mut self`:

```rust
impl PendingReviewPost {
    pub fn approve(&mut self) -> Option<Post> {
        self.approvals += 1;
        if self.approvals < 2 {
            None
        } else {
            Some(Post{content: self.content})
        }
    }
}
```

But then I got an other error:

```text
error[E0507]: cannot move out of borrowed content
  --> src/lib.rs:34:32
   |
34 |             Some(Post{content: self.content})
   |                                ^^^^ cannot move out of borrowed content
```

Indeed, what happens is that `approve()` is mutating `self`.
So nothing stop us from mutating `self.content` in ``approve()`. But we can't both modify the content *and* move it out.

# First attempt

I then changed the `Post` struct to hold references to strings instead:

```rust
pub struct Post<'a> {
    content: &'a str
}

impl<'a> Post<'a> {
    pub fn new() {
        // ...
    }

    pub fn content(&self) -> &str {
        &self.content
    }

}

impl PendingReviewPost {
    pub fn approve(&mut self) -> Option<Post> {
        self.approvals += 1;
        if self.approvals < 2 {
            None
        } else {
            Some(Post{content: &self.content})
        }
    }
}
```

And then I tried a new version of the production code.

We'll approve the pending post, then retrieve the `Option` and check if we have an approved content to publish:

```rust
fn try_publish(pending_post: Option<Post>) {
    if let Some(approved_post) = pending_post {
        println!("Publishing {}", approved_post.content());
    } else {
        println!("Post not ready ...")
    }
}

fn main() {
    let mut post = Post::new();
    post.add_text("I ate a salad for lunch today");
    let mut pending_post = post.request_review();
    let maybe_post = pending_post.approve();
    try_publish(maybe_post);
}
```

```console
$ cargo run
Post not ready ...
```

OK, this works.

Let's add a second call to `approve()`:

```rust
fn main() {
    // ..
    let mut pending_post = post.request_review();
    let maybe_post = pending_post.approve();
    try_publish(maybe_post);
    post = pending_post.approve();
    try_publish(maybe_post);
}
```

```text
error[E0499]: cannot borrow `pending_post` as mutable more than once at a time
  --> src/main.rs:19:22
   |
17 |     let maybe_post = pending_post.approve();
   |                      ------------ first mutable borrow occurs here
18 |     try_publish(maybe_post);
19 |     let maybe_post = pending_post.approve();
   |                      ^^^^^^^^^^^^ second mutable borrow occurs here
...
24 | }
   | - first borrow ends here

```

Hu-oh. Now rust complains that we've two mutable references in the same scope.

# The command/query separation violation

That's when I realized: the `approve()` function is doing two different things:

* One it mutate the state of the `PendingReviewPost`.
* Two, it returns an `Option`.

This is called a command/query separation violation because in a give function you should either:

* Modify the internal state and return nothing (that's a "command")
* Or, return a value but have no side-effect (that's a "qurey")

So instead of getting the result directly from the `approve()` function, I split it in two:

```rust
impl PendingReviewPost {
    pub fn approve(&mut self) {
        self.approvals += 1;
    }

    pub fn get_post(&self) -> Option<Post> {
        if self.approvals < 2 {
            None
        } else {
            Some(Post{content: &self.content})
        }
    }
```

So the production code had to change too:

```rust
fn try_publish(pending_post: &PendingReviewPost) {
    if let Some(approved_post) = pending_post.get_post() {
        println!("Publishing {}", approved_post.content());
    } else {
        println!("Post not ready ...")
    }
}

fn main() {
    // ...
    let mut pending_post = post.request_review();
    pending_post.approve();
    try_publish(&pending_post);
    pending_post.approve();
    try_publish(&pending_post);
}

```

Now it works because the `get_post()` does not mutate the `pending_post` so we can get several immutable references to it.

# Conclusion

That's was my first experience with the `rust` programming language. I must say I'm very impressed by the quality of the documentation and the contents of the book. I also found the messages of the compiler quite clear and useful.

The fact that the compiler guided be towards a more clean architecture is a big bonus. By writing code in rust, you'll have to think about topics like ownership and mutability, and this will help you write code that is both safer and more efficient in a bunch of other occasions. (Like when writing C++ or even Python code).

Cheers!
