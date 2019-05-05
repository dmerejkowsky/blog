---
authors: [dmerej]
slug: dmenv
date: 2019-02-04T14:34:30.324519+00:00
draft: true
title: "dmenv"
tags: [python]
summary: ....
---

# Intro

<!-- idea 1 -->

On October 31, 2018, back from work, I started working on a new Rust project. It was *supposed* to be a quick proof of concept. Little did I know that several months later, this project will be used in production


<!-- idea 2 -->

The Python packaging ecosystem is a mess. There are tons of projects trying to improve the situation but they are big and complicated. What if I told you there was a new kid in town, that is both fast, simple and as powerful as all the alternatives?


<!-- idea 3 -->

Most Python projects need *both* a `setup.py` and a way to specify development dependencies (running tests, building documentation) and so on. They can use `requirements.txt`, or `Pipfile` or `tox.cfg` but if they do they will have to synchronise things with the `setup.py` by hand. *poetry* solves the problem by *not* using `setup.py` ever but you are screwed if you want to build FFI modules or something like this.

So let's start at the beginning: what do we really need?

# How it works

# Go try

Star the GitHub project ...
