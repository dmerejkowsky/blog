---
authors: [dmerej]
slug: my-blogging-flow-part-2-publishing
date: 2019-02-07T12:14:20.273365+00:00
draft: true
title: "My Blogging Flow - Part 2 - Publishing"
tags: [misc]
summary: How this blog gets written - part 2
---

Everything starts with an idea. I have a small git repository on my dedicated machine which contains a bunch of markdown files, one per article. (This repository is private by the way).

The contents of these files can vary from just a few lines, to an almost complete article. Most of the time they only contain a basic outline though.

I update the `ideas` repository as soon as ideas come. You won't believe how fast you can forget what or how you wanted to say something otherwise.

Next it's time to start writing the full article. I have a [small Python script](post.py) which:

* finds out the next article number and fill up the front matter for me (because I'm lazy)
* runs `git add` on the generated Markdown file so I don't delete it by mistake by running `git clean` (because mistakes happen)
* opens the Markdown file in Neovim

Now it's time to draft the article. I always do it from Neovim

<!--more-->
