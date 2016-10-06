---
date: 2016-10-01T15:36:12+02:00
draft: false
title: Thoughts on Changelogs
---

Some time ago at work someone suggested we start using a template for our `git`
commit messages, based on what the [Angular project](https://angularjs.org/) does.

The rules are documented in the [CONTIRBUTING.md page](
https://github.com/angular/angular.js/blob/master/CONTRIBUTING.md#commit-message-format)
on github.

In a nutshell, here's what the commit messages look like:

```
* feat($anchorScroll): convert numeric hash targets to string
* docs(ngCsp): fix "directive"'s `restrict` and hide comment from output
* refactor($resource): use `route.defaults` (already merged `provider.defaults` + `options`)
```

We decided to start using this too, and someone on the team said:
"Great! That way we can use a script to generate changelogs!"

<!--more-->

## Keep a CHANGELOG

Some one on the Internet[^1] already said it:
[Don’t let your friends dump git logs into CHANGELOGs™](
http://keepachangelog.com/en")

Feel free to read the page, there's tons of helpful advice.

Here's what the authors say about just using git log`messages:

> _Why can’t people just use a git log diff?_

> Because log diffs are full of noise —  by nature. They could not make a
> suitable change log even in a hypothetical project run by perfect humans who
> never make typos, never forget to commit new files, never miss any part of a
> refactoring. The purpose of a commit is to document one atomic step in the
> process by which the code evolves from one state to another. The purpose of a
> change log is to document the noteworthy differences between these states.

Put in an other way : git log messages are useful amongts developers _inside_
your project. They'll use the git log to understand _why_ a particular change
was made, either during review, or when they run `git blame` on a file.

On the other hand, the changelog is meant to help developers _outside_ the
project. They'll use it to understand why something broke after they upgrade,
or simply when they try to figure out if it's worth upgrading at all.

Since the target audience of the git log messages and the changelog are so
different, I believe you simply can't use one to generate the other.

## Some changelog tips

Here are a few additional tips I'd like to share.

### Ordering

The items in the git log messages are of course always sorted chronologically.
[^2]

In a changelog, sections are also sorted chronologically, but
_inside_ a section, you may want to sort them in a different order, like so:

```markdown

# Version 3.0 (2016-10-01)

## Highlights

* Some new feature here <link to the documentation>
* A critical security bug fix there <link to the CVE>

## Other Bug fixes

* A minor bug fix here <link to the bug>

## Breaking changes

```

That's an other good reason why you can't directly use git log messages for this.
(I'm not a big fan of sections named "added", "remooved", "changed", "fixed", but your
mileage may vary)

### When to update the Changelog

The page also says:

> Always have an "Unreleased" section at the top for keeping track of any
> changes.
>
> This serves two purposes:
>
> * People can see what changes they might expect in upcoming releases
>
> * At release time, you just have to change "Unreleased" to the version number and add
> a new "Unreleased" header at the top.

It's easy to enforce this during code review: when someone commits something
that is worth documenting for the outside users, make them update the changelog
in the same commit, or in a commit right after it.

If you wait until right before publishing a new release, you may have a hard
time remembering exactly what changed and why.

Also, by forcing people to update the changelog when they break
retro-compatibility (which is one of the most valuable things to have in a
changelog), you'll have an opportunity to:

* Make sure the breaking change is properly documented (aka: what will I have to
  fix if I upgrade?)
* Discuss whether a backward-compatibility layer may be implemented.

### Using the Changelog

Making a new release of any project is exciting, and you're eager to tell the
world about it.

But, *please*, when this occurs, include a link to your changelog in your
annoncement!

It really bothers means when I see a `foo 1.3 is out!` on twitter or on a
mailing list but with no links to the actual Changelog at all.

See you next time!

[^1]: [Olivier Lacan](http://olivierlacan.com/), to be precise :)
[^2]: Well, almost. You can amend your commits and change the date any way you like.
