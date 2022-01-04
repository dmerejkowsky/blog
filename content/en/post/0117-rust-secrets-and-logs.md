---
authors: [dmerej]
slug: rust-secrets-and-logs
date: 2022-01-04T10:11:47.416699+00:00
draft: false
title: "Is Rust worth learning? Part 1: logs and secrets"
tags: [rust]
summary: Is Rust worth learning? Let's find out. A story based on real events.
---


> A language that doesn't affect the way you think about programming, is not worth knowing.
>  -- Alan J. Perlis - Yale University

To see if Rust is worth trying, then, let me tell you a story - based on real events.

# Logs and secrets

Let's say you are writing a Java application that needs to make HTTP calls on an external API.

To do this, you have a client class that implements a `call` method.

```java
public class Client {
  private void authenticate(String appSecret) {
    //
  }

  private void doRequest(String url) {
    //
  }

  public void call(String appSecret, String url) {
    authenticate(appSecret);
    doRequest(url);
  }
}
```

Note that you need do send an `app secret` along the url to make the call, hence the separate `authenticate()` method.

You also have a Config record to hold the configuration of the application:

```java
public record Config(String appSecret, String url) {
}
```

Finally, you have a main class that reads the values from the environment, builds a Config and a Client instances and uses it to make calls:

```java
public class App {
  public static void main(String[] args) {
    String appSecret = System.getenv("APP_SECRET");
    String url = System.getenv("API_URL");
    Config config = new Config(appSecret, url);

    Client client = new Client();
    client.call(config.appSecret(), config.url());
  }
}
```

Since logs are important, you also add a call to `logger.info()` when making the call:

```java
public void call(String appSecret, String url) {
  authenticate(appSecret);
  logger.info("Making the call"); // <- new
  doRequest(url)
}
```


# A vulnerability happens

You push the code into production, and some time later you get assigned to the following bug in the issue tracker:

```
BUG: APP_SECRET found in the logs
SEVERITY : critical
PRIORITY : high

The logs sent by the application at startup contains the
APP_SECRET

...
INFO: config: Config[appSecret=s3cret, url=https://api.dev]
...
INFO: Making the call
```

So you take a look at the code base, and sure enough, you find the problem: someone from an other team added a log containing the contents of the Config class:

```java
// SomewhereElse.java

logger.info("config:" + config.toString());
```

Sure, the bug is easy to fix. You can just remove the call to `logger.info`.

But after thinking about it more, you decide to also override the `toString()` method of the `Config` struct so that the app secret is *always* redacted:

```diff
public record Config(...) {
+  @Override
+  public String toString() {
+    return String.format("Config[appSecret:REDACTED, url:%s]", this.url);
+  }
}
```

There. You can mark the bug as "fixed" and move to something else, like take a look at this new programming language called Rust ...

A few hours later, here's what you learned.

# Ownership

First, Rust has this notion of *ownership*: every piece of data must have exactly one owner. By default, data is *moved* and can't be used after the move.

Here's an example:

```rust
struct StringOwner {
   inner: String, // <- note: fields are private by default
}

fn main() {
  let s = String::from("hello"); // Creates a new string

  let owner = StringOwner { inner: s }; // Move the string into
                                        // the 'StringOwner' struct

  println!("{}", s); // Compile error: cannot use the string after it's moved
}
```

Second, if you don't want to move the value, you have to "borrow" it.

```rust
fn borrow_the_string(s: &String) { // < Note the '&'
   //
}

fn main() {
  let s = String::from("hello"); // Creates a new string

  borrow_the_string(&s); // Note the '&'

  println!("{}", s); // OK
}
```

This is a immutable (or shared) borrow: you won't be able to modify the string.

You've also learned about mutable (or exclusive) borrows. They would allow you to modify the string, but they are not relevant for this story.

## The trait system

You also learned that classes don't exist in Rust. Instead, Rust uses *traits*, and adds methods to structs using `impl` blocks:

```rust
/* in stuff.rs */

// This says that the Stuffer trait
// contains a method named do_stuff
pub trait Stuffer {
   fn do_stuff(&self);
}

struct Foo {
  // ...
}

// This says that Foo implements the Stuffer trait,
// and than compilation will fail if do_stuff() is not present
// or has not the proper signature
impl Stuffer for Foo {
  fn do_stuff(&self) {
    // Implementation here
  }
}
```

The trait must be in the scope where you are using it:

```rust
use stuff::Foo;

let foo = Foo::new():
foo.do_stuff(); // Error: Stuffer trait is not in scope
```

```rust
use stuff::Foo;
use stuff::Stuffer; // <- new

let foo = Foo::new():
foo.do_stuff(); // OK: Stuffer trait is in scope
```


# A rewrite

So, feeling adventurous, you decide to try and re-implement your application in Rust, just to feel like how the code would look like and if you can find a better way of handling the security issue you had to fix in Java.

You start with the `Config` class:

```rust
struct Config {
  url: String,
  app_secret: String,
}
```

Then you add the `Client class`:

```rust
struct Client {
  // ...
}

impl Client {
  fn authenticate(&self, app_secret: String) {
    // ...
  }

  fn do_request(&self, url: String) {
    // ...
  }

  fn call(app_secret: String, url: String) {
      self.authenticate(app_secret);
      info!("{}", "Making the call");
      self.do_request(url);
  }
}
```

And finally, the main() function:

```rust
fn main() {

    let app_secret = std::env::var("APP_SECRET").unwrap();
    let url = std::env::var("API_URL").unwrap();

    let config = Config { app_secret, url };

    let client = Client;
    client.call(config.app_secret, config.url);
}
```

"Well, that was easy" you think. "I wonder what people mean when they're talking about 'fighting the borrow checker'".

Then you try to use `client.call` a second time:

```rust
fn main() {

    let client = Client;
    client.call(config.app_secret, config.url);
    // ...
    client.call(config.app_secret, config.url); // <- new
}
```

```txt
error[E0382]: use of moved value: `config.app_secret`
  --> src/main.rs:27:17
   |
23 |     client.call(config.app_secret, config.url);
   |                 ----------------- value moved here
...
27 |     client.call(config.app_secret, config.url);
   |                 ^^^^^^^^^^^^^^^^^ value used here after move
```

"Oh, right", I need to "borrow" the `app_secret` and the `url` in the client if I want to be able to keep using the config struct.

So you change the code to be like this instead:

```diff
  impl Client {
-     fn call(&self, app_secret: String, url: String) {
+     fn call(&self, app_secret: &str, url: &str) {
          //
      }

  }

-    client.call(config.app_secret, config.url);
+    client.call(&config.app_secret, &config.url);
```

There. Now the client *borrows* the app secret and the url and the code compiles and runs fine.

Feeling confident, you try and reproduce the logging issue.

First, you add a `#[derive(Debug)]` annotation on top of the `Config` struct:

```diff
+ #[derive(Debug)]
  struct Config {

  }
```

And then you add a log displaying the contents of the config struct:

```diff
  fn main() {
    let config = Config { app_secret, url };
+   info!("config: {:?}", &config);
   }
}
```

This code works because Rust knows how to print debug representations of strings and booleans and the `derive(Debug)` annotation can automatically generates the code to print a debug representation of the `Config` struct.

Indeed, the code compile, and, sure enough, the secret shows up in the log:


```text
[INFO] config: Config { app_secret: "s3cret", url: "https://api.dev" }
[INFO] Making the call to https://api.dev
```

OK, you've reproduced the problem. But can you find a better solution this time?

# Time to think

You've heard good things about Rust type system, so you wonder: "Would it be possible to solve the problem by adding a new type?".

You start with a `SecretString` struct:

```rust
struct SecretString {
    inner: String,
}

impl SecretString {
    fn new(inner: String) -> Self {
        Self { inner }
    }
}
```

The constructor takes ownership of the string, which is a good thing, because it means the inner value *can no longer be accessed* once the `SecretString` struct is created:

```rust
let secret_value = std::env::var("APP_SECRET").unwrap();
let app_secret  = SecretString::new(secret_value):

dbg!(secret_value); // < does not compile!
```

Then you change the type of `app_secret` in Config from `String` to `SecretString`:

```diff
struct Config {
-    app_secret: String,
+    app_secret: SecretString,
}
```

Which means you have to get the inner value when authenticating the client:

```diff
impl Client {
-   fn call(&self, app_secret: &str, url: &str) {
-   self.authenticate(&app_secret);
+   fn call(&self, app_secret: &SecretString, url: &str) {
+      self.authenticate(app_secret.inner);
+   }

}
```

You are then faced with 2 compile errors:

First, the `Debug` macro no longer works:
```
error[E0277]: `SecretString` doesn't implement `std::fmt::Debug`
  --> src/main.rs:26:5
   |
24 | #[derive(Debug)]
   |          ----- in this derive macro expansion
25 | struct Config {
26 |     app_secret: SecretString,
   |     ^^^^^^^^^^^^^^^^^^^^^^^^ `SecretString` cannot be formatted using `{:?}`
   |
   = help: the trait `std::fmt::Debug` is not implemented for `SecretString`
```

To fix this, you implement the debug trait yourself:

```rust
use std::fmt::Debug;
// ^-- new - remember: traits needs to be in scope
// in order to use them


impl Debug for SecretString {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "REDACTED")
    }
}
```

Second, you can't use the `inner` field directly in the `call()` method:

```
error[E0616]: field `inner` of struct `SecretString` is private
  --> src/client.rs:13:39
   |
13 |         let secret_value = app_secret.inner;
   |                                       ^^^^^ private field
```

So you add a public method to access the inner value:


```rust
impl SecretString {
    pub fn expose_value(&self) -> &str {
        &self.inner
    }
}
```

And you fix the client code:

```rust
pub fn call(&self, app_secret: &SecretString, url: &str) {
    let secret_value = app_secret.expose_value(); // <- new!
    self.authenticate(&secret_value);
}
```

# Going further

Then you think back about the rule about traits having to be in scope, and you decide to move the `expose_value` method into a trait:

```rust
pub trait ExposeSecret {
    fn expose_value(&self) -> &str;
}

impl ExposeSecret for SecretString {
// ^--  used to be `impl SecretString`

    fn expose_value(&self) -> &str {
        &self.inner
    }
}
```

And then the compiler says:

```
error[E0599]: no method named `expose_value` found for reference
`&SecretString` in the current scope
  --> src/client.rs:13:39
   |
13 |         let secret_value = app_secret.expose_value();
   |                                       ^^^^^^^^^^^^

   = help: items from traits can only be used if the trait is in scope
   = help: the following trait is implemented but not in scope; perhaps add a
           `use` for it:

use crate::secrets::ExposeSecret;
```

So you comply:

```rust
use crate::secrets::ExposeSecret; // <- new!
use crate::secrecy::SecretString;
```

There - the code compiles, and it's now pretty hard to leak the app secret:

Indeed, if a value has been wrapped in the SecretString struct, anyone attempting to access it must:

* call a method that *sounds* dangerous (`expose_value()`)
* import a trait that *also* sounds dangerous (`secrets::ExposeSecret`)

It's also very easy to edit the code for safety: just list the usages of the `ExposeSecret` trait.

# Conclusion

I hope you found this post interesting: it shows how you can use some unique features of the Rust programming language to tackle an old issue in a novel way.

I mentioned at the beginning that the this post is based on true stories, so here are my two sources of inspiration:

* The issue of a secret value exposed by mistake is based on an actual security vulnerability I reported to the Miniflux maintainers. You can see the details in the [miniflux repository](https://github.com/miniflux/v2/commit/87d58987a698296fa4306ed43e8400568edd51f1).
* The `SecretString` struct is based on a real crate, called [secrecy](https://docs.rs/secrecy/latest/secrecy/).

Thanks for taking this journey with me, and if you're a reading this while trying to fix the log4j security vulnerability, you have my sincere sympathy :)

Cheers!

