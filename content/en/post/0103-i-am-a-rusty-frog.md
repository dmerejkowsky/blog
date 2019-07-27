---
authors: [dmerej]
slug: i-am-a-rusty-frog
date: 2019-07-27T09:46:51.113571+00:00
draft: false
title: "I am a rusty frog"
tags: [misc, rust]
summary: >
 A story about lack of optimisation and the weaknesses
 of the human mind.
---

Do you know the fable of the frog and the boiling water? It goes like this:

> If you drop a frog in a pot of boiling water, it will of course frantically try to clamber out. But if you place it gently in a pot of tepid water and turn the heat on low, it will float there quite placidly. As the water gradually heats up, the frog will sink into a tranquil stupor, exactly like one of us in a hot bath, and before long, with a smile on its face, it will unresistingly allow itself to be boiled to death.

At least that's how Daniel Quinn's tells it in *The Story of B*.

It is a powerful metaphor, although if you read the [Wikipedia article](https://en.wikipedia.org/wiki/Boiling_frog), it turns out frogs do not actually behave that way.

But I think there's still some truth it in: if you experience some increasing pain gradually enough, you may not realizing how much you are actually suffering until it's too late. At least it's what happened to me.

Let's start at the begining, before we start talking about Rust, refactoring, performance bugs and the weaknesses of the human mind.

# Part 1: The setup

A long time ago, I realized I spent far too much time typing `cd` to navigate between project directories, and that the default `ctrl-r` binding for `zsh` was a bit awkward to use for me.

Then I realized I could solve both of those problems by writing two very similar commands: `cwd-history` and `cmd-history`.

Let's talk about the former. It's a command-line tool that takes two actions, `add`  and `list`. Here's how it works:

* `cmd-history add` takes one parameter and adds it to a "database" in `~/.local/share/dm-tools/commands-history`. The database is just a file with one command per line.
* `cmd-history list` simply dumps the contents of the database to `stdout`.
* Then,  there's a `zsh` hook to run right after a command has been read and is about to be executed. In the hook, `cmd-history add` is called with the text of the last command.
* Finally, `zsh` is configured so that when `ctrl-r` is pressed, the output of `cmd-history list` is piped through `fzf` and then the selected command is run.

I use a similar program called `cwd-history` that does exactly the same thing but for the working directories. It runs in another zsh hook called `chpwd`, and is triggered by typing the command `z`[^1].

There are a few specificities like making sure the entries are not duplicated or ensuring that every symlink in the added path is resolved, but we'll get to that later.

# Part 2: RIR

The two programs were written in Python and shared a ton of functionality but since I am a lazy programmer I did not bother with refactoring the code.

But something was bugging me. There was a small noticeable delay whenever I was using them, particularly on old hardware. So I decided to try and rewrite them in Rust. And surely when I measured the performance, there was a *huge* difference in the startup time: Rust compiles directly to machine code, and there was no need to wait for the Python interpreter to start. I was happy.

# Part 3: the Kakoune switch

A few months ago, I switched from Nevoim to [Kakoune](https://kakoune.org/) for my main text editor and was faced with a problem.

Kakoune does not have any persisting state by design, and I was missing a particular vim feature that allowed me to quickly select any recently opened file (aka. <abbr title="Most Recently Used">MRU</abbr> files).

But I already knew how to solve that! I wrote yet another tool called `mru-files` for reading and writing the MRU files in another database, and write a bit of Kakoune script:


```bash
# Call `mru-files add` with the buffer name when opening a new buffer
hook global BufOpenFile .* %{ nop %sh{ mru-files add  "${kak_hook_param}" } }

# Call `mru files list` when pressing <leader key>o:
map global user o
  -docstring 'open old files'
  ':evaluate-commands %sh{ mru-files list --kakoune }<ret>'
```

Note the `--kakoune` option when calling `mru-files list`: we need to call the `menu` command so that we can present the list of MRU files to the user and open the file when it's selected.

It looks like this:

```
menu
  "/foo.txt" "edit -existing 'foo.txt:'"
  "/bar.txt" "edit -existing 'bar.txt'"
  ...
```

While I was it, I also added a `--kakoune` argument to `cwd-history list` so that I could switch to previously visited directories directly from Kakoune:

```bash
 map global cd o
   -docstring 'open old working directory'
   ':evaluate-commands %sh{ cwd-history list --kakoune }<ret>'
```

# Part 4: the refactoring

So now I was faced with *three* very similar code written in Rust. It was time for a refactoring [^2].

Here's what I did:

* First, I added a trait called `EntryCollection` that contained methods named `add` and `list`

```rust
pub trait EntriesCollection {
    fn add(&mut self, entry: &str);
    fn list(&self) -> &Vec<String>;
}
```

* The trait was implemented by three structs: `Commands`, `WorkingDirs` and `MruFiles`.

```rust
pub struct Commands {
    entries: Vec<String>,
}

impl EntriesCollection for Commands {
  // ...
  fn add(&mut self, entry: &str) {
      // Deduplicate the entry and store it in self.entries
      // ...
  }

  fn list(&self) -> Vec<String> {
      // return self.entries
  }
}
```

```rust
pub struct WorkingDirs{
    entries: Vec<String>,
}

impl EntriesCollection for WorkingDirs {
   // ...
   fn add(&mut self, entry: &str) {
         // Convert the entry to a path, check  if it exists,
         // then canonicalize it and insert it in self.entries
   }
}
```

(and similar code for MruFiles)

* I wrote a `Storage` struct to interact with the database:

```rust
impl Storage {
    pub fn new(
        mut entries_collection: Box<EntriesCollection>,
        path: &std::path::PathBuf,
    ) -> Storage {
        let db_path = path.join(entries_collection.name());
        let entries = read_db(&db_path);
        for entry in entries {
            entries_collection.add(&entry);
        }
        Storage {
            db_path,
            entries_collection,
        }
    }

    pub fn list(&self) -> &Vec<String> {
        &self.entries_collection.list()
    }

    pub fn add(&mut self, entry: &str) {
        &mut self.entries_collection.add(&entry);
        write_db(&self.db_path, &self.list())
    }

```


* I wrote `StorageManager` struct to instantiate the `Storage` struct with the correct `EntriesCollection` implementation depending on a `StorageType` enum:

```rust

pub enum StorageType {
    CwdHistory,
    CommandsHistory,
    FilesHistory,
}

pub struct StorageManager {
   // ...
}

impl StorageManager {
    pub fn new(storage_type: StorageType) -> Self {
            let entries: Box<EntriesCollection> = match storage_type {
                StorageType::CwdHistory => Box::new(WorkingDirs::new()),
                StorageType::CommandsHistory => Box::new(Commands::new()),
                StorageType::FilesHistory => Box::new(MruFiles::new()),
            };


        };

        let storage = Storage::new(entries, &app_dir);
        StorageManager { storage }
    }

    pub fn list(&self) {
        // Delegates to self.storage.list()
    }

    pub fn add(&mut self, entry: &str) {
        // Delegates to self.storage.add()
    }

}
```

* And finally, I wrote three `main` functions that called the `StorageManager` constructor, passing it the enum variant.

```rust
// In src/bin/cmd-history.rs
use dm_tools::StorageType;
fn main() {
    // ...
    dm_tools::run_storage_manager(StorageType::CommandsHistory)
}
```

```rust
// In src/bin/cwd-history.rs
use dm_tools::StorageType;
fn main() {
    // ...
    dm_tools::run_storage_manager(StorageType::CwdHistory)
}
```

```rust
// In src/bin/mru-files.rs.rs
use dm_tools::StorageType;
fn main() {
    // ...
    dm_tools::run_storage_manager(StorageType::FilesHistory)
}
```

And that was my first mistake: I forgot to measure performance *after* the refactoring. I was *sure* the code was correct. After all, if it compiles, it works, right?

And sure enough, the code *did* work. I could open MRU files and old project directories from Kakoune, and I was quite pleased with myself.

Of course, by now you should have guessed there's a horrible performance bug in the code above. Did you spot it? If you did, congrats! I certainly did not at the time.

# Part 5: The peer programming session

The refactoring took place 6 months ago. I am using those tools at work, which means I was using those commands for 6 months, 5 days a week. The database files contained thousands of entries. The horrible bug was still there, consuming CPU cycles without a care in the world, and I did not notice anything.

Fortunately, I did a peer programming session with one of my colleagues and something weird happened. It got *bored* watching my zsh prompt getting stuck when I was using the `z` and `ctrl-r` shortcuts.

I then measured the performance of my tools again and I found  that the `cmd-history list` command took 1.7 **seconds** to run.  That's *one thousand and seven hundred* milliseconds. It's a **very long** time. No wonder my colleague got bored! What's amazing though is that I did *not* notice anything wrong until he told me about it.

# Part 6: The fix

Now it's time to squash the bug. The culprit lies here, in the `Storage` constructor:

{{< highlight rust "hl_lines=8-10" >}}
impl Storage {
    pub fn new(
        mut entries_collection: Box<EntriesCollection>,
        path: &std::path::PathBuf,
    ) -> Storage {
        let db_path = path.join(entries_collection.name());
        let entries = read_db(&db_path);
        for entry in entries {
            entries_collection.add(&entry);
        }
        Storage {
            db_path,
            entries_collection,
        }
    }
}
{{</ highlight >}}


We're reading each line of the database file, and passing it to `EntriesCollection.add()`. This means we keep calling the `add()` method over and over. It does not do much, but it still has to go through *all* the entries when performing deduplication. This is a classic case of the [Shlemiel algorithm](https://www.joelonsoftware.com/2001/12/11/back-to-basics/) and it explains the abysmal performance of the tool as soon as the database gets big enough.

I believe I wrote the code that way because I thought it would be nice to somehow "validate" the entries when reading the database. That way, if the algorithm in the `add` method changed, the database will be migrated automatically. Another classical mistake named *<abbr title="You Ain't Gonna Need It">YAGNI<abbr>*: it's doubtful I'll ever need to migrate the database, and when I need to, I'll probably just have to write a tiny throw-away script to do it.

Anyway, now that we've decided the "automigrating" feature can go away, we can solve our performance issue by adding an `add_all` method to the trait, and replacing the `for` loop in the `Storage` constructor:

{{< highlight rust "hl_lines=3" >}}
 pub trait EntriesCollection {
     fn add(&mut self, entry: &str);
+    fn add_all(&mut self, entres: Vec<String>);
     fn list(&self) -> &Vec<String>;
}
{{</ highlight >}}

{{< highlight rust "hl_lines=8-11" >}}
impl Storage {
    pub fn new(
        mut entries_collection: Box<EntriesCollection>,
        path: &std::path::PathBuf,
    ) -> Storage {
        let db_path = path.join(entries_collection.name());
        let entries = read_db(&db_path);
-       for entry in entries {
-           entries_collection.add(&entry);
-       }
+       entries_collection.add_all(entres);
        Storage {
            db_path,
            entries_collection,
        }
    }
}
{{</ highlight >}}

In turn, this means we need to implement the `add_all()` method on all structs:

```rust
impl EntriesCollection for Commands {
    // ...
    fn add_all(&mut self, entries: Vec<String>) {
        self.entries = entries;
    }
}
```

```rust
impl EntriesCollection for WorkingDirs {
    // ...
    fn add_all(&mut self, entries: Vec<String>) {
        self.entries = entries;
    }
}
```

```rust
impl EntriesCollection for MruFiles {
    // ...
    fn add_all(&mut self, entries: Vec<String>) {
        self.entries = entries;
    }
}
```

# A small digression

Surely you've noticed the implementation of `add_all()` is *exactly* the same in the three structs. Why did not we add blanket implementation of the `add_all()` method in the trait?

Well, because we need access to the `entries` field of the struct, and there's no way to do that in Rust. Since I'm in love with Rust, I can rationalize this in several ways:

* First, the code duplication is not that a problem since there's only one line of code.
* Second, the duplication is *incidental*. We could imagine using a `Set` instead of a `Vec` to store the entries, and the trait does not need to know about this. Ditto if we decide to rename the field.
* Third, I can tell myself that this lacking feature is a good thing[^3] because I've often been bitten in other languages when sharing class members through inheritance (both in C++ and Python).

Take those how you want: I can tell myself those are good arguments, but you don't have to believe me :)

# The moral of the story

Here are my takeaways:

* When performance matters, don't forget to measure it constantly, especially after refactorings (or even after each commit if you can afford to)
* The boiling frog metaphor is actually a good one, and you may be inside some boiling water without realizing it.
* And finally, listen to what people say to you when they tell you about something bad in your life. I actually felt something was off with my machine those last 6 months, but it took an other person to help me take a step back and understand what was wrong.

Take care and see you another time!

[^1]: That's because I was using a tool named `z` before I decided to [re-implement it myself]({{< relref "0041-rewriting-z-from-scratch.md" >}}).
[^2]: If you are wondering why, go read *[The Rule of Three](https://blog.codinghorror.com/rule-of-three/)* on the Coding Horror blog.
[^3]: By the way, not all Rust users think this way. You can find a RFC about using fields in traits [on GitHub](https://github.com/nikomatsakis/fields-in-traits-rfc).
