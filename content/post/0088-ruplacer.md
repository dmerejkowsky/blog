---
authors: [dmerej]
slug: ruplacer
date: 2018-10-14T12:34:43.722319+00:00
draft: false
title: "ruplacer: find and replace text in source files"
tags: [rust]
summary: Introducing ruplacer, a command line tool that finds and replaces text in source files.
---

# Introduction

Today I'd like to talk about a command-line tool I've been working on.

It's called [ruplacer](https://github.com/SuperTanker/ruplacer) and as the name suggest, it's *rually* cool and written in Rust.

Basically, it finds and replaces text in source files. Here's a screenshot of ruplacer in action:

![ruplacer screenshot](/pics/ruplacer.png)

Some nice features:

* Skips files listed in `.gitignore`, as well as binary files
* Runs in dry run mode by default (use `--go` to actually write the changes to the filesystem)
* Defaults to searching the current working directory, although an other path maybe specified after the pattern and the replacement.
* Uses Rust regular expressions, which means you can capture groups in the pattern and use them in the replacement. For instance:

```shell
# Replaces dates looking like DD/MM/YYYY to YYYY-MM-DD
$ ruplacer '(\d{2})/(\d{2})/(\d{4})' '$3-$1-$2'
```
* Can be run with `--no-regex` if the pattern is just a substring and should not be used as a regular expression
* Last, but not least  there's also a `--subvert` mode, which allows you to perform replacements on a variety of case styles:

```shell
$ ruplacer --subvert foo_bar spam_eggs
Patching src/foo.txt
-- foo_bar, FooBar, and FOO_BAR!
++ spam_eggs, SpamEggs, and SPAM_EGGS!
```


# How it works

Here's how it works:

First, we build a [structopt](https://crates.io/crates/structopt) struct for the command-line arguments parsing. Depending on the presence of the `--subvert` or `--no-rexeg` flags, we  build a *Query*, which can be of several types: `Substring`, `Regex` or `Subvert`.

Then we leverage the [ignore](https://crates.io/crates/ignore) crate to walk through every file in the source directory  while skipping files listed in `.gitignore`. By the way, the ignore crates comes directly from [ripgrep](https://github.com/BurntSushi/ripgrep), an awesome alternative to `grep` also written in Rust.

Along the way, we build a *FilePatcher* from the source file and the query. The FilePatcher goes through every line of the file and  then sends it along with the query to  a *LinePatcher*.

The LinePatcher runs the code corresponding to the query type and returns a new string, using the [Inflector](https://crates.io/crates/Inflector) to perform case string conversions if required.

Finally, if the string has changed, the FilePatcher builds a *Replacement* struct and pretty-prints it to the user. While doing so, it also keeps a recod of the modified contents of the file. Finally, if not in dry-run mode, it overwrites the file with the new contents.

And that's pretty much it :)


# Why I'm sharing this

The idea of ruplacer started almost a decade ago when a colleague of mine showed me a shell function called `replacer` (thanks, Cédric!) It was basically a mixture of calls to `find`, `sed` and `diff`. You can still [find it online](https://github.com/cgestes/ctafconf/blob/78b92a60bc185b73f95418e3e913e33aae8799f6/bin/replacer#L75).

Because I wanted better cross-platform support, a dry-run mode and a colorful output, I rewrote it in Python a few years ago. Along the way, the features, command line syntax and the style of the output changed quite a lot, but I've been using it regularly for all this time.


Finally, after hearing about ripgrep and [fd-find](https://github.com/BurntSushi/ripgrep), I decided to give Rust a go, and that's how ruplacer, the third incarnation of this tool, was born. This makes me confident it's good enough for *you* to try.

If you have `cargo` installed, you can get ruplacer by running `cargo install ruplacer`. Otherwise, you will find the [source code](https://github.com/SuperTanker/ruplacer/tree/master/src) and [pre-compiled binaries](https://github.com/SuperTanker/ruplacer/releases) on GitHub.

Cheers!
