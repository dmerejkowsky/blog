---
slug: introducing-rusync
date: 2018-05-08T17:59:06.225602+00:00
draft: false
title: "Introducing rusync"
tags: [rust]
---

Today I wrote my first "real" rust project.

It's a re-write of `rsync` in Rust called `rusync`.

Here's what its installation and usage look like:

```
$ cargo install rusync
$ rusync test/src test/dest
:: Syncing from test/src to test/dest …
-> foo/baz.txt
-> foo/bar.txt
 ✓ Synced 2 files (1 up to date)
```

You can find the sources [on github](https://github.com/dmerejkowsky/rusync).

# Feedback request

I wrote this because I wanted to give Rust a try.

If you're already are a Rust developer, I'd appreciate it if you could give me a honest review of the code I wrote.

See the [feedback page]({{< ref "pages/feedback.md" >}}) for all the possible ways to reach me, and many thanks in advance!

# What's next

Here's a list of features I plan to implement

* Symlinks handling
* Option to delete extraneous files
* Global progress bar

The last one is interesting: we need to recursively walk through all the files in the source folder in order to estimate the total size of the transfer, but we want to do that *while the transfer is in progress*.

That will be an opportunity to play a little bit with Rust concurrency features :)

Cheers!
