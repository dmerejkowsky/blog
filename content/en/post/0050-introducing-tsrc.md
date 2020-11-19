---
authors: [dmerej]
slug: introducing-tsrc
date: "2017-07-31T12:11:39.599298+00:00"
draft: false
title: Introducing tsrc
tags: ['python', 'git']
summary:
  |
  Introducing `tsrc`, a tool to manage multiple git repositories and
  automate GitLab interaction.
---

# Introduction

Handling source code versioning in a software company is challenging. You have to decide
how to organize your sources.

The first method is to put everything in a giant repository.

The second method is to split the sources across multiple repositories.

Both methods have their pros and cons.

With the "giant repository" approach you sometimes cannot use existing source
control software like git, because they do not scale enough for very large
projects, or you have to make your own patches, like
[facebook does with Mercurial](
https://code.facebook.com/posts/218678814984400/scaling-mercurial-at-facebook/).

With multiple repositories it gets easier to just use git as usual,
but you'll likely need a tool on top of it so that working with multiple
repositories is easier.

A popular solution for the second case is to use git submobules, but:

 * You need a 'master' repository on top of the workspace

 * When you update a submobule, you have to make a commit in the parent
   repository too, and this step is easy to skip.

Also, we found out that to make sure all the repositories are in a consistent
state, we could simply push the same tag on several repositories.


# tsrc

Enter [tsrc](https://github.com/TankerApp/tsrc). We use it everyday
at [Tanker](https://tanker.io) to manage our sources.

It has a nice and intuitive user interface that takes care of running
`git` commands for you in multiple repositories.

It also features (optional) commands to interact with GitLab.

Let's see how it works.

{{< note >}}
We will only be showing the basic usage of some tsrc commands.
You can use `--help` to discover all the available options.
{{</ note >}}


# Installation

`tsrc` is written in Python3 and can be installed with `pip`:

```console
# Linux
$ pip3 install tsrc --user
$ Add ~/.local/bin to PATH

# macOS
$ pip3 install tsrc --user
$ Add ~/Library/Python/3.x/bin to PATH

# Windows
$ pip3 install tsrc
# PATH is already correct: it is set by the Windows installer
```

You can find the sources on [github](https://github.com/TankerApp/tsrc).

# Usage

## Cloning the repositories

`tsrc` is driven by a **manifest** file that contains the names and paths of
repositories to clone.

It uses the `YAML` syntax and looks like:

```yaml
repos:
  - src: foo
    url: git@gitlab.local:acme/foo

  - src: bar
    url: git@gitlab.local:acme/bar
```

The manifest must be put in a git repository too. You can then use the following
commands to create a new workspace:

```console
$ mkdir ~/work
$ cd work
$ tsrc init git@gitlab.local:acme/manifest.git
```

In this example:

* `foo` will be cloned in `<work>/foo` using `git@gitlab.com/acme/foo.git` origin url.
* Similarly, `bar` will be cloned in `<work>/bar` using `git@gitlab.com:acme/bar.git`

## Making sure all the repositories are up to date

You can update all the repositories by using `tsrc sync`.

* The manifest itself will be updated first.
* If a new repository has been added to the manifest, it will be cloned.
* Lastly, the other repositories will be updated.

Note that `tsrc sync` only updates the repositories if the changes are trivial:

* If the branch has diverged, `tsrc` will do nothing. It's up to you to use
  `rebase` or `merge`
* Ditto if there is no remote tracking branch

This way, there is no risk of data loss or sudden conflicts to appear.

(By the way, this is a good example on how to implement this directive
from the Zen of Python: **"In the face of ambiguity, refuse the temptation to guess"**.)

So that you know where manual intervention is required, `tsrc sync` will also
display a summary of errors at the end:

![tsrc sync](/pics/tsrc-sync.png)


## Managing merge requests

Since we do most of our operations from the command line, it's convenient to be
able to do GitLab operations from the shell too.

We leverage the GitLab REST API to create and accept merge requests.

For instance, here is how you can create and assign a merge request:

```console
# start working on your branch
$ tsrc push --assignee <an active user>
```

When the review is done, you can accept it and let GitLab
merge the branch once the CI passes with the following command:

```console
$ tsrc push --accept
```

Note how `--accept` will _not_ merge the pull request immediately. This is by
design. We believe that continuous integration is only worth it if it _prevents_
bad code from landing into `master`, thus we make sure you cannot by-pass the CI.

## Other goodies

### tsrc status

You can use `tsrc status` to quickly get an overview of the status of your
workspace:

![tsrc status](/pics/tsrc-status.png)

### tsrc foreach

Sometimes you just want to run the same command on every repositories.

`tsrc` has you covered:

```console
$ tsrc foreach -- some-command --some-opts
```

(Note the `--` token that separates the options of `some-command` from the
options of `tsrc`)


### tsrc log

If you have multiple repos, chances are you are going to use several of them
when doing a release, so you'll probably end up putting the same tag on several
repos.

Thus, you may want to quickly get an overview of everything that changed between
two tags.

That's where `tsrc log` comes in handy. It will run `git log` with nice
color options and present you a summary:

![tsrc log](/pics/tsrc-log.png)


# Conclusion

We hope you'll find this tool handy for your own projects.

Feel free to try it, contribute, and give us feedback.


*Update: The project now has a [documentation](https://tankerapp.github.io/tsrc/)
and a [FAQ](https://tankerapp.github.io/tsrc/faq/)!*
