---
authors: [dmerej]
slug: optimistic-merging
date: "2021-09-11T14:36:46.126712+00:00"
draft: true
title: "Applying Optimistic Merging"
tags: [misc]
summary: |
 I decided to try and implement Optimistic Merging for the open source
 project I maintain - here's why.
---

# Introduction - Pessimistic Merging

If you've contribute to an open-source project on GitHub or GitLab, or
write code inside for a company, you are probably familiar with the
concept of "Pessimistic Merging" - you write a patch (or a pull request
or a merge request), but it is not merged right away. For it to be
merged you need to wait for human approval to be given and/or continuous
integration to pass.

I can think of several reasons why this strategy is often the one which is used:

* It's used by really big projects for quite some time
* It's kind of the *default* way to collaborate on a platform like GitHub or GitLab
* There are even tools like Gerrit which work by specifying a list of
* constraints before a patch can be merged [^1] - which is used among other
  things, Google's Android Open Source Project or the Qt framework

There's also the fact that it allows to enforce some rules. Used with source control like Git,
Pessimistic Merging can ensure:

* A "clean" git history (from the commit messages to their contents to the size of the patches)
* A consistent coding style
* A test suite that always pass on the main development branch
* A code that is composed of patches that have been reviewed and
* approved by an arbitrary number of people
* ... and so on

And indeed, there are some projects where this matters a lot - in a corporate environment, or in
a "sensitive" project like a browser, a database engine or an operating system ...

That being said, we rarely talk about the *downsides* of Pessimistic
Merging (and you'll probably never think that this concept needed a *name*).

# Issues with Pessimistic Merging

For this, I'll let you read the article which prompted me to write this
one: [Why Optimistic Merging Works Better](http://hintjens.com/blog:106) [^2]

The idea behind Optimistic Merging is very simple: you *merge the patch first*, and
*then* deal with issues like broken builds, code style violation and other problems.

Sure, this means that the main development branch of your Git repository may now contain
commits that do not fully work, code that does not always compile, or commits that only
fix whitespace.

But for a medium-sized project, that does nothing too security-sensitive, and for which
maintainers and collaborators are hard to find - is it such a bad deal?

Note that most users of your projects will only use tagged releases, so
the bad history is only an issue for direct contributors of the project.

See also Aleksey Kladov's piece on [Two Kinds of Code
Review](https://matklad.github.io/2021/01/03/two- kinds-of-code-
review.html) - which is the reason I learned about Optimistic Merging in
the first place and wanted to try it out.

A note before I continue: they are plenty of cases where using
Pessimistic Merging *is* the best strategy - in my case, I've decided to
use Optimistic Merging only for the open- source projects *I* maintain,
and I'm not suggesting you should do too. I'm just describing an
alternate strategy you may or may not find better for your case.

## My workflow for Optimistic Merging

### Setting the stage

I'm the maintainer of a project called "foo", written in Python, and
hosted in GitHub.

The project uses `flake8` as a linter to catch small mistakes, the code
is formatted with `black`, and it has has some tests (of course).

It is also *very easy* to run the linters, the tests and the code
formatter from the developer machine (this will matter later on).

Here comes a developer I never heard of named Mallory and they open
their first ever merge request to the GitHub repository.

### Merging Mallory's changes

The first step is for me to get the proposed changes on my local machine.

Since it's a PR on GitHub, I can do something like this, where "some-branch"
is the *source ref* of Mallory's PR:

```bash
$ git remote add mallory git@github.com:mallory/foo
$ git fetch mallory
From github.com:mallory/foo
* [new branch] some-branch -> mallory/some-branch
```

Then I try and rebase `some-branch` on top of the main branch. This
allows me to make sure the commits can be merged right away.

Best case scenario: Mallory already rebased or merge their branch on top of main
and there are no conflicts :)

Worse case scenario: I spend some time fixing some conflicts, no big
deal - at this point I've been fixing conflicts during `git rebase` for
more than 10 years - why would I impose that to a new contributor ?
Sure, they'll be a moment when Mallory will *have* to master git rebase,
but does it need to be *right now*? What if it's their first patch ever?

Anyway, during the rebase I can take a look at each commit. Since everything
is on my machine, it's trivial to amend Mallory's commits if a linter complains.

It's also trivial to run `black .` after each commit.

If I feel I need to, I can also choose to run the tests to make sure that the
commit did not break anything.

Also, if there's a small issue (like a misleading comment) *I can fix
it right away!* - why go through the hassle of telling Mallory they did
something wrong, *then* wait for them to update the merge request,
*then* re-start the process from scratch?

Finally, I keep a simple text file opened with some *notes* for later
use (you'll see in a moment)

When all of this is done, it's time to push Mallory's branch. I re-run
the linters and the tests just to be sure, then I push the code and
leave a message in the PR telling Mallory the changes have been merged.

## Looking at the interaction from Mallory's point of view

It's very likely Mallory's was not paid to write the patch, but they still
worked on it and thought their work was good enough to open a pull request.

They probably don't know much about the project, and it's likely they
don't know everything about Git, Python, flake8 or black - and it's even
possible they know nothing about testing!

Yet, the first reply they got for the maintainer is "Thanks! Your
commits have been merged". Boom. The collaboration is already working.

What a great start!

Contrast with a typical response when using PM,  which would look like this:

> hank you for contribution, but the CI does not pass (test_foo_bar4 is
> failing and there are some lint error). Also, please merge or rebase
> your work on top of the main branch so that the merge is fast-forward".

... followed by a bunch of nitpicks about the merge request.


## After the merge

Anyway, now it's time to put my notes to good use.

If there are some trivial changes I have to do, I can just tell Mallory:

> It was a good idea to refactor the do_stuff() method inside the Foo class,
> but you did not adapt the doc string, which I've done in commit ...

Again, we're *working together* here, and I'm willing to bet Mallory is
more likely to watch their docstrings next time they write a new patch

If there was some non-trivial changes (like a missed opportunity for a
refactoring), I can just create an issue with a task list for instance.

# Conclusion

To me, there's something deeply satisfying about Optimistic Merging -
not sure why, maybe it has something to do with my recent teaching
experiences?

Another great thing about Optimistic Merging (I think) is that it
*frees* you from the constraint of whatever tool you are using.

You see, there's a "pressure" from GitHub interface that's heavily targeted
towards Pessimistic Merging (which again may not be a bad thing, depending
on your project), and using Optimistic Merging forces you to think
"outside" of the GitHub "box".

By the way, you may have noticed that my Optimistic Merging workflow
requires *very little features* from whatever platform I'm using to host
the code (I'm not even doing the code review form the web interface !).
This is not a coincidence, but will be the topic for an other blog post.
Stay tuned.


[^1]: Fun fact: to do this,  Gerrit embeds [an implementation of the Prolog Language](https://gerrit-review.googlesource.com/Documentation/prolog-cookbook.html)