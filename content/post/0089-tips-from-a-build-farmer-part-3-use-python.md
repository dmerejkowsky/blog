---
authors: [dmerej]
slug: tips-from-a-build-farmer-part-2-some-concepts
date: 2018-08-28T18:17:04.151310+00:00
draft: true
title: "Tips From a Build Farmer - Part 3: Use Python"
tags: [ci]
summary: Why you should consider writing your CI scripts in Python
---

[Last time]({{< ref "post/0084-tips-from-a-build-farmer-part-2-some-concepts.md" >}}) we asked ourselves: "What language should I use to write CI scripts?".

Based on my experience, (I've been writing and maintaining CI scripts for almost 10 years): there's only one good answer: Python.

I've seen CI scripts written in Bash, Powershell or even Batch, I've re-written many of them in Python, and it has *always* paid off big time.

Does this mean *you* should rewrite your own scripts too? Definitely not! Don't base your decisions based solely on the experience of *one individual*. Just keep reading and hopefully the arguments and example I'll be given here will help you to take the correct decision.
