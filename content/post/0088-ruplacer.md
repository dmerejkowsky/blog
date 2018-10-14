---
authors: [dmerej]
slug: ruplacer
date: 2018-10-14T12:34:43.722319+00:00
draft: true
title: "ruplacer: find and replace text in source files"
tags: [rust]
summary: Introducing ruplacer, a command line tool that finds and replaces text in source files.
---

# Introduction: switching from User to Account

Let's say you've written a big application in your favorite language.

You've just [you should never have Users](), by Itamar, so you decide to rename all usages of the class 'User', to a new class named 'Account'.

# The powerful IDE

Let's see what happens if you try to perform this task from an IDE:

* First, you navigate to the 'User' class definition
* You enter the shortcut for the "Refactor/Rename" feature
* You type the new name: 'Account'
* Maybe you to interact with the GUI to specify a few options. If you're lucky, you can sometimes see a preview of the changes before they happen.
* Then you wait.
* Then you realize you still have a UserAccessor class, and you redo the whole thing.

This is tedious.

(Or at least, *I* find it tedious, especially because for every IDE the way to do this always changes slightly. If you *really* don't mind, well, ruplacer is not for you.)

# The mighty shell

Maybe you're one of these people who thinks some things can and should be done from the command line.

In this case, welcome to the club!

*"No need for stinkin' IDE"* you say. *"Behold! The power of composing shell pipelines to achieve your goal with simple tools!"*

And then you type:

```
find . -type f -exec sed -i "" -e s/User/Account/g {} \;
```

And because your rock, you're able to enter this without making any mistakes.

For the muggles, this means:

* Find (`find`) every file (`-type f`) in the current directory (`'.'`)
* Then for each file, exececute (`-exec`) the following command: `sed -i -e s/User/Account/g <filename>`.
* The `\;` at the end is here because `find` needs it for some reason. (Don't ask ...).


And what does sed does?

* It runs inplace (`-i`), meaning it will modify the file given as argument, and then it:
* Executes (`-e`) the following sed code: `s/User/Account/g` on each line of the file.

And what does the `s/User/Account/g` sed code does?

* It does a "global" (`g`) "substitution" (`s`), using `/User/` for the regular expression to search for each line, and `Account` for the replacement to use. [^1]

Phew! What a loads of weird syntax to know about! Plus, this time you have no way to preview the changes before they happen.

If you know `fd`, I can hear you say: *"Just use `fd` instead of find. Look how simpler the syntax is!"*:

```
$ fd --type file --exec sed -i ""e 's/User/Account/g' {}
```

True, the syntax is less weird: no need of `\;`, no need to specify the directory (the current working dir is used by default), and as a bonus, hidden files and files listed in the `.gitignore` will be skipped.

The fact is, you still need to remember the sed syntax, which, by the way, varies from an operating system to another!


# ruplacer to the rescue

And here's where ruplacer comes in. It's good at one thing and one thing only: find and replace text in source files.

Here's how to use it:

```shell
$ cargo install ruplacer
$ ruplacer old new
Patching tests/data/a_dir/sub/foo.txt
-- sub/foo: old is everywhere, old is old
++ sub/foo: new is everywhere, new is new
-- old is really old
++ new is really new

Patching tests/data/top.txt
-- Top: old is nice
++ Top: new is nice

Would perform 3 replacements on 2 matching files

# If the diff looks ok, re-run ruplacer with the `--go` option:
$ ruplacer User Account --go
...
Performed 3 replacements on 2 matching files
```

ruplacer and `fd` are quite similar:

* They're both written in Rust, so they are fast.
* The both defaults to the current working directory, although you can pass a directory after the pattern and the replacement.
* They both only look at files that are not listed in the `.gitignore`

Note how we keep the 'preview feature' of the IDE by just having a "dry-run" mode by default and a `--go` option.

ruplacer uses Rust regular expressions by default, which means you can do things like this:

```shell
# Replace ugly MM/DD/YYYY dates by YYYY-MM-DD
$ ruplacer '(\d{2})/(\d{2})/(\d{4})' '$3-$1-$2'
```

If you don't like this behavior, you can use a `--fixed-strings` option and ruplacer will only deal with lines that merely *contains* the `pattern` as a substring.

Finally, inspired by the great [Abolish vim plugin]() by Tim Pope, ruplacer also has a `--subvert` option.

For instance:

```patch
$ ruplacer --subvert foo_bar spam_eggs
-- this is foo_bar, an instance of the FooBar class
++ this is spam_eggs, an instance of the SpamEggs class
```

And that's all there is to it.

# Why I'm sharing this

The idea of ruplacer started almost 10 years ago when a colleague of mine showed me a shell function called `replacer`. Thanks, Cédric!

Since then, I've re-written it in Python (twice!). Along the way the features, command line syntax and the style of the output changed quite a lot, but I've been using it regularly for all this time.

ruplacer is the third version of this tool, which makes me confident it's good enough for *you* to try.


You will find the source code and pre-compiled binaries of ruplacer on github.

Cheers!

[^1]: This comes from the 'ed' editor, from which both sed and vim derive, and that's why you would type mostly the same thing in vim.
