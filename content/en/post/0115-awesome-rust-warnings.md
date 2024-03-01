---
authors: [dmerej]
slug: awesome-rust-warnings
date: "2021-02-02T13:35:21.074236+00:00"
draft: false
title: "Two awesome Rust warnings"
tags: [rust]
summary: Why I love the Rust compiler
---

# Introduction

If you've ever used a compiler (or any other tool) that can produce warnings about your code, you may be used to messages that are hard to understand, confusing or just plain wrong.

But today I want to show you that good compiler warnings do exist and how they can make your code more correct.

# The incorrect server API

The first example comes from code I wrote to test the Rust implementation of the Tanker client SDK. You don't need to know precisely how Tanker works to follow this example - let's just say the client needs a "Tanker permanent identity" from an identity server to start a session. [^1]

In my case, the identity server was already written in Go using the Gin-Gonic framework.

Here's what the implementation of the `sign_in` route looked like:

```go
// This struct is used by various Gin handlers
type UserResponse struct {
	UserID              string `json:"user_id"`
	Email               string `json:"email"`
	PermanentIdentity   string `json:"tanker_permanent_identity"`
}


// handler for the /sign_in route
func (this *Server) signIn(c *gin.Context) {
	var body SignInBody
	jsonErr := c.BindJSON(&body)
	if jsonErr != nil {
		c.JSON(400, gin.H{"error": jsonErr.Error()})
		return
	}

	email := body.Email
	password := body.Password

	// Not shown: check email and password, fetch user from the db

	userResponse := UserResponse{
		Email:               user.Email,
		UserID:              user.UserID,
		PermanentIdentity:   user.PermanentIdentity,
	}

	c.JSON(200, userResponse)
}
```

To parse the JSON response from the server in the Rust client, I used serde, like this:

```rust
#[derive(Deserialize)]
struct UserResponse {
    user_id: String,
    email: String,
    tanker_permanent_identity: String,
}

impl Client {
    pub async fn sign_in(&mut self) -> Result<()> {
        let email = ...;
        let password = ...;

        let mut data = HashMap::new();
        data.insert(String::from("email"), email);
        data.insert(String::from("password"), password);

        let response = self.client.post("/sign_in", data).await?;
        let user_response = response.json::<UserResponse>().await?;

        self.start_tanker(&user_response).await?;
    }

    async fn start_tanker(&self, user_response: &UserResponse) -> Result<()> {
        let private_identity = &user_response.tanker_permanent_identity;
        let email = &user_response.email;
        let status = self.tanker.start(&private_identity).await?;
        // Not shown: verify identity by email when required

        Ok(())
   }
}
```

When I first compiled the code, I got this warning:

```
Warning: field is never read: `user_id`
  --> src/notepad.rs:24:5
   |
24 |     user_id: String,
   |     ^^^^^^^^^^^^^^^
   |
   = note: `#[warn(dead_code)]` on by default
```

This made sense: as you can see, to start a Tanker session we only need the `email` and `tanker_permanent_identity` fields of the JSON response returned by the server. In particular, we don't need the user ID at all.

What's interesting with this example is that at Tanker, we already wrote *six other clients* for the server in question (using Python, Go, Java, JavaScript, Objective-C and Ruby) and that was the first time we got an indication that our JSON API was wasting bandwidth by sending information that was actually not needed!


# The useless mutation

The second example comes from a personal project - a week ago I started implementing an interpreter in Rust, following the instructions from the [Writing an Interpreter in Go](https://interpreterbook.com/), by Throsten Ball.

As I worked on the the lexer, I wrote the following code:

```rust
use std::iter::Peekable;
use std::str::CharIndices;

#[derive(Debug)]
pub(crate) struct Lexer<'a> {
    code: &'a str,
    iter: Peekable<CharIndices<'a>>,
}

impl<'a> Lexer<'a> {
    pub fn new(code: &'a str) -> Self {
        Self {
            iter: code.char_indices().peekable(),
            code,
        }
    }

    // ...

    /// Try to read an identifier starting at start_pos
    fn read_identifier(&mut self, start_pos: usize) -> &'a str {
        // end_pos is either `None` if we reached the end of the input code,
        // or Some(index) if we reached a character that is not part of
        // of a valid identifier

        let mut end_pos = Some(start_pos);
        loop {
            // Is the next character valid?
            let peek = self.iter.peek();
            match peek {
                Some((next_pos, next_c)) if Self::is_valid_ident(*next_c) => {
                    // Yes: advance next_pos
                    end_pos = Some(*next_pos);
                    self.iter.next();
                }
                Some((next_pos, _)) => {
                    // No: advance next_pos and exit the loop
                    end_pos = Some(*next_pos);
                    break;
                }
                None => {
                    // There's no next character : we've reached the end
                    // of the input code
                    end_pos = None;
                    break;
                }
            }
        }

        match end_pos {
            // end_pos is None: return all the code from start_pos to the end
            None => &self.code[start_pos..],
            // end_pos is not None: return the code from start_pos to end_pos
            Some(index) => &self.code[start_pos..index],
        }
    }
}
```

Here's what the compiler had to say:

```
warning: value assigned to `end_pos` is never read
   --> src/lexer.rs:131:13
    |
131 |         let mut end_pos = Some(start_pos);
    |             ^^^^^^^^^^^
    |
    = note: `#[warn(unused_assignments)]` on by default
    = help: maybe it is overwritten before being read?

warning: value assigned to `end_pos` is never read
   --> src/lexer.rs:136:21
    |
136 |                     end_pos = Some(*next_pos);
    |                     ^^^^^^^
    |
    = help: maybe it is overwritten before being read?
```

The second warning was the easiest to fix: we keep setting `end_pos` to
`Some(*next_pos)` but never read it until the loop exits. So we can just
remove the line that sets `end_pos` before calling `self.iter.next()`:


```diff
    fn read_identifier(&mut self, start_pos: usize) -> &'a str {
        let mut end_pos = Some(start_pos);

        loop {
              match peek {
-                 Some((next_pos, next_c)) if Self::is_valid_ident(*next_c) => {
-                     end_pos = Some(*next_pos);
+                 Some((_, next_c)) if Self::is_valid_ident(*next_c) => {
                      self.iter.next();
                  }
                  Some((next_pos, _)) => {
                      end_pos = Some(*next_pos);
                      break;
                  }
                  None => {
                      end_pos = None;
                      break;
                  }
              }
        }

```

But the compiler was still unhappy:

```
warning: value assigned to `end_pos` is never read
   --> src/lexer.rs:131:13
    |
131 |         let mut end_pos = Some(start_pos);
    |             ^^^^^^^^^^^
    |
    = note: `#[warn(unused_assignments)]` on by default
    = help: maybe it is overwritten before being read?
```

This took me a while to realize, but the compiler is telling me that I can
declare the `end_pos` binding but not initialize it right away:

```diff
    fn read_identifier(&mut self, start_pos: usize) -> &'a str {
-       let mut end_pos = Some(start_pos);
+       let end_pos;
        loop {
              match peek {
                  Some((_, next_c)) if Self::is_valid_ident(*next_c) => {
                      end_pos = Some(*next_pos);
                      self.iter.next();
                  }
                  Some((next_pos, _)) => {
                      end_pos = Some(*next_pos);
                      break;
                  }
                  None => {
                      end_pos = None;
                      break;
                  }
              }
        }
```

I love this : the `end_pos` binding is no longer `mut`, and can *only* be assign a value in two cases:
either in the `None` arm of the `match peek` block, or to `end_pos` when the peek character is not valid.

It's much less likely for the code to be buggy!

# Conclusion

I hope those two examples gave you an idea of what it's like to write code using a language
that has such a focus on *correctness* and how nice it is to have *useful* warnings.

For now, Rust is the only language I've used which gave me this feeling of "the compiler has my back",
but I'm sure they are others - please tell me bellow if you know one.

And if this gave you a motivation to try and learn Rust, go for it!


[^1]: More info in the [Tanker documentation](https://docs.tanker.io/latest/)
