---
authors: [dmerej]
slug: optimistic-merging
date: "2021-09-14T16:06:46.126712+00:00"
title: "Optimistic Merging In Practice"
tags: [misc]
summary: |
 I decided to try and implement Optimistic Merging for the open source
 project I maintain - here's why.
---

# Introduction - Pessimistic Merging

If you've contributed to an open-source project on GitHub or GitLab, or written code for a company, you're probably familiar with the concept of "Pessimistic Merging". You write a patch (or a pull request or a merge request), but it is not merged (or applied) right away. Instead, you need to wait for human approval to be given and/or for continuous integration to pass.

I can think of two reasons why this strategy is often the one which is used:

1. It's been used by really big projects (like the Linux kernel) for quite some time
2. It's kind of the *default* way to collaborate on platforms like GitHub or GitLab

There are even tools like Gerrit which work by specifying a list of constraints before a patch can be merged [^1] - which is used among other things by Google's Android Open Source Project or the Qt framework.

There's also the fact that it allows to enforce some rules. Used in combination with source control software (like Git), Pessimistic Merging can ensure:

* A "clean" git history (from the commit messages to their contents to the size of the patches)
* A consistent coding style
* A test suite that always pass on the main development branch
* A code that is composed only of patches that have been reviewed and approved by an arbitrary number of people
* ... and so on

And indeed, there are some projects where this matters a lot - in a corporate environment, or in a "sensitive" project like a browser, a database engine or an operating system ...

That being said, we rarely talk about the *downsides* of Pessimistic Merging - which is why you probably never thought that this concept needed a *name*.

# Issues with Pessimistic Merging

For this, I'll let you read the article which prompted me to write this one: [Why Optimistic Merging Works Better](http://hintjens.com/blog:106) [^2].

The idea behind Optimistic Merging is very simple: you *merge the patch first*, and *then* deal with issues like broken builds, code style violation and other problems.

Sure, this means that the main development branch of your Git repository may now contain commits that do not fully work, code that does not always compile, or commits that only fix code styling errors.

But for a small or medium-sized project, that does nothing too security-sensitive, and for which maintainers and collaborators are hard to find - is it such a bad deal?

On this topic, see also Aleksey Kladov's piece on [Two Kinds of Code Review](https://matklad.github.io/2021/01/03/two-kinds-of-code-review.html) (which is the reason I learned about Optimistic Merging in the first place and wanted to try it out), where he explains how pull requests are reviewed and merged for the rust-analyzer project.

A note before I continue: they are plenty of cases where using Pessimistic Merging *is* the best strategy - here I'm just describing an alternate strategy you may find interesting.

With that out of the way, let's now look how Optimistic Merging works for me in practice.

## My workflow for Optimistic Merging

### Setting the stage

I'm the maintainer of a project called "foo", written in Python, and hosted in GitHub.

The project uses `flake8` as a linter to catch small mistakes, the code is formatted with `black`, and it has has some tests (of course). It is also *very easy* to run the linters, the tests and the code formatter from the developer machine (this will matter later on).

Here comes a developer I never heard of (let's call them Mallory) - and they open their first ever merge request to the GitHub repository.

### Merging Mallory's changes

The first step is for me to get the proposed changes on my machine and to prepare a list of notes for later feedback - a simple text file is enough.

Since it's a PR on GitHub, I can do something like this, where "some-branch" is the *source ref* of Mallory's PR:

```bash
$ git remote add mallory git@github.com:mallory/foo
$ git fetch mallory
From github.com:mallory/foo
* [new branch] some-branch -> mallory/some-branch
```

Then I rebase `some-branch` on top of the main branch. This allows me to make sure the commits can be merged without conflicts.

During the rebase I look at each commit diff and I take notes.

Since everything is on my machine, it's trivial to amend Mallory's commits if a linter complains or to run `black` if I need to.

I can also choose to run the tests locally if I fear a commit may have caused a regression.

Finally, if there's a small issue (like a misleading comment) I can fix it right away! There's no need to go through the hassle of:

* telling Mallory they did something wrong,
* waiting for them to update the merge request,
* re-starting the process from scratch.

When all of this is done, it's time to push Mallory's branch. I re-run the linters and the tests just to be sure, then I push the code and leave a message in the PR discussion telling Mallory the changes have been merged.

### Looking at the interaction from Mallory's point of view

It's very likely that Mallory was not paid to write the patch, (this is a medium-size open-source project, after all) but they still worked on it and thought their work was good enough to open a pull request.

They probably don't know much about the project, and it's likely they don't know everything about Git, Python, flake8 or black. And it's even possible they know nothing about testing!

Yet, the first reply they got for the maintainer is "Thanks! Your commits have been merged". Boom - the collaboration is already working - what a great start!

Contrast with a typical response when using Pessimistic Merging,  which would look like this:

> Thank you for your contribution, but the CI does not pass (test_foo_bar4 is failing and there are some lint errors). Also, please merge or rebase your work on top of the main branch so that the merge is fast-forward.

... followed by a bunch of nitpicks about the merge request.


### After the merge

Anyway, now it's time to put my notes to good use.

If there are some trivial changes I had to do, I can just tell Mallory:

> It was a good idea to refactor the do_stuff() method inside the Foo class, but you did not adapt the doc string, which I've done in commit ...

Again, we're *working together* here, and I'm willing to bet Mallory is more likely to watch their docstrings next time they write a new patch :)

If there was some non-trivial changes (like a missed opportunity for a refactoring), I can just create an issue with a task list for instance.

I can also start a pull request and have *Mallory* review it.

# Conclusion

To be frank, I've just started implementing this strategy for my open-source projects, so it's a bit early to draw any conclusions. That being said, so far it has been going great, and I wanted to share the idea of Optimistic Merging right way.

I'll let you know how it goes in the future. Until then, happy coding!

[^1]: Fun fact: to do this,  Gerrit embeds [an implementation of the Prolog Language](https://gerrit-review.googlesource.com/Documentation/prolog-cookbook.html)
[^2]: If you have trouble with opening this link, make sure you are using the http:// URL, the https:// version is  unfortunately broken.
