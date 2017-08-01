---
slug: introducing-tsrc
date: 2017-07-31T12:11:39.599298+00:00
draft: true
title: Introducing tsrc
tags: ['python', 'git']
summary:
  |
  Introducing `tsrc`, a tool to manage multiple git repositories and
  automate GitLab interaction.
---

# Introduction

When you are working in a software company, you have two choices for how you
organize your sources.

The first method is to put everything in a giant repository, that keeps getting
bigger and bigger.

The second method is to split the sources across multiple repositories.

Both methods have their pros and cons. With the "giant repository" approach you
cannot use popular DVCS like git (it just does not scale).
With multiple repositories you can use git, but you need a tool on top of
it so that working with multiple repositories is easier.

A popular solution for the second case is to use git submobules, but
the UI of `git submobule` is not very nice and it's easy to make mistakes.

# tsrc

Enter [tsrc](https://github.com/TankerApp/tsrc). We use it everyday
to manage our sources at [Tanker](https://tanker.io)

At is core, all it does is parse configuration files and running appropriate git
commands.

Let's see how it works.

# Installation

`tsrc` is written in Python3 and can be installed with `pip`:

```console
$ pip3 install tsrc --user
```

You can find the sources on [github](https://github.com/TankerApp/tsrc).

# Usage

## Cloning the repositories

To know the URLs and paths of the repositories to clone, `tsrc` reads a
**manifest** file. It uses the `YAML` syntax and looks like:

```yaml
format: 1

gitlab:
  url: http://10.100.0.1:8000

clone_prefix: git@gitlab.local

repos:
  - src: foo
    name: acme/foo
    copy:
      - src: bar.txt
        dest: top.txt

  - src: bar
    name: acme/bar
```

The manifest should be put in a git repository too. And then you can use:

```console
$ mkdir ~/work
$ cd work
$ tsrc init git@gitlab.local:acme/manifest.git
```

In this example,

* `foo` will be cloned in `<work>/foo` using `git@gitlab.com/acme/foo.git` origin url.
* Similarly, `bar` will be cloned in `<work>/bar` using `git@gitlab.com:acme/bar.git`
* The file ``bar.txt`` will be copied from the `bar` repository to the
  top of the workspace, in `<work>/top.txt`

## Making sure all the repositories are up to date

You can update all the repositories by using `tsrc sync`.

The manifest itself will be updated first.

If a new repository has been added to the manifest, it will be cloned.

Then the following commands will be run for each repository:

```console
$ git fetch --tags --prune origin
$ git merge --ff-only @{u}
```

Those two commands:

* Make sure all the tags are fetched
* Prune the branches that have been removed from the remote
* Only update the branches if they are fast-forward.
  (That's what `--ff-only` and `@{u}` are about)

That way `tsrc sync` only updates the repositories if the changes are trivial:

* If the branch has diverged, `tsrc` will do nothing. It's up to you to use
  `rebase` or `merge`
* Ditto if there is no remote tracking branch (when `@{u}` does not match
  anything)

Note this is a good example on how to implement this directive
from the Zen of Python: **"In the face of ambiguity, refuse the temptation to guess"**.

`tsrc sync` will also display a summary of errors at the end:

![tsrc sync](/pics/tsrc-sync.png)

## Managing merge requests

* Generate a token from GitLab

* Add the *http* url to the manifest:

```yaml
gitlab:
  url: http://gitlab.local
```

* Create a `~/.config/tsrc.yml` looking like:

```yaml
auth:
  gitlab:
    token: <YOUR TOKEN>
```


* Start working on your branch

* Create the pull request

```console
$ tsrc push --assignee <an active user>
```

* When the review is done, tell GitLab to merge it once the CI passes

```console
$ tsrc push --accept
```

Note how `--accept` will _not_ merge the pull request immediately. This is by
design. We believe that continuous integration is only worth it if it _prevents_
bad code from landing into `master`, thus we make sure you cannot by-pass the CI.

## Other goodies

### tsrc foreach

Sometimes you may want to run the same command on every repositories.

There are two ways to do that:

```console
$ tsrc foreach -- some-command --some-opts
```

(Note the `--` token that separates the options of `some-command` from the
options of `tsrc`)

In this form, we will use something like this:

```python
for repo in workspace.enumerate_repos():
    subprocess.run(["some-command", "--some-opts"], cwd=repo)
```

For this to work, `some-command` should be a "real binary".

The other way is to use the `-c` option, which will run the command as a string
into a shell. (Bash on Linux and macOS, cmd.exe on Windows), for instance:

```console
$ tsrc foreach -c "cd src && touch some-file"
```

In this form, we'll use:

```python
for repo in workspace.enumerate_repos():
    subprocess.run("cd src && touch some-file", cwd=repo, shell=True)
```

### tsrc log

If you have multiple repos, chances are you are going to use several of them
when doing a release, so you'll probably end up putting the same tag on several
repos.

Thus, you may want to quickly get an overview of everything that changed between
two tags.

That's where `tsrc log` comes in handy. It will run `git log` with nice
color options and present you a summary:

![tsrc log](/pics/tsrc-log.png)

### tsrc status

You can use `tsrc status` to quickly get an overview of the status of your
workspace:

![tsrc status](/pics/tsrc-status.png)

# Conclusion

I hope you'll find this tool handy for your own projects.
