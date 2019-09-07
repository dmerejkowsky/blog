---
authors: [dmerej]
slug: how-i-use-git
date: 2017-07-22T08:58:57.132376+00:00
draft: false
title: How I Use Git
tags: ["git"]
toc: true
---

Welcome!

This article will be a guided tour of how I use git.

We'll talk about configuration of git itself, the aliases and
scripts I've written, and the other tools I work with.

<!--more-->

Since this article is quite long, here's a table of contents:

* [Introduction](#introduction)
* [Options](#options)
* [Aliases](#aliases)
* [Helper scripts](#helper-scripts)
* [Gui tools](#gui-tools)
* [Neovim](#neovim)

# Introduction

## Talk is cheap, show me the code

Everything can be found in my [dotfiles repo](
https://github.com/dmerejkowsky/dotfiles/blob/master/configs/git/config).

Feel free to read, but please don't use it directly: the code was written to be
used by only one person: me. Unless you are my hidden tween brother, it's very
likely to be _not_ suited for you.

## Location of the config files

I prefer having my git configuration files in `~/.config/git/config` rather than
in `~/.gitconfig`.

That's a matter of personal taste, of course, but it's also conforming to the
[XDG directory specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-0.6.html)

## Why did you bother writing this?

Several reasons:

* People seem to like it when I talk about theses things (as seen by the
  relative success of the [How I Lint My Python](
  {{< ref "/post/0037-how-i-lint-my-python.md" >}}) article)
* When describing my configuration files and work flows to others, I tend to
  find things that can be improved.
* I always hope you can learn a few things from my experience (otherwise, why
  would I share&nbsp;it?)

With this out of the way, let's dive in!

## Options

### Excluding files

I like to keep a separate list of file patterns I always want to
ignore, without to touch the `.gitignore` of all the projects I contribute to:

```ini
# in ~/.config/git/config
[core]
excludesfile = ~/.config/git/excludes
```

```text
# in ~/.config/git/excludes
# Vim
*.swp

# QtCreator
CMakeLists.txt.user
*.autosave
```


### rerere

`rerere` stands for *replay recorded merge resolution*.

You have to explicitly enable it:
```ini
[rerere]
enabled = true
```
Let's see it in action:

* I'm working on a branch called `new-feature`, which started one week ago.
* I decided to rebase against the latest `master` version:

```console
$ git fetch origin
$ git rebase oirigin/master
First, rewinding head to replay your work on top of it...
Applying: new feature
...
CONFLICT (content): Merge conflict in bar.txt
Recorded preimage for 'bar.txt'  # <---- rerere
error: Failed to merge in the changes.
Patch failed at 0001 new feature
$ git mergetool
# fix conflicts
$ git rebase --continue
Applying: new feature
Recorded resolution for 'bar.txt'. # <--- rerere
```

Thus, assuming both `master` and `new-feature` continue to change
and we need to re-run `git rebase`:

```console
$ git rebase origin/master
 bar.txt | 1 +
 1 file changed, 1 insertion(+)
First, rewinding head to replay your work on top of it...
Applying: new feature
....
Falling back to patching base and 3-way merge...
Auto-merging bar.txt
CONFLICT (content): Merge conflict in bar.txt
Resolved 'bar.txt' using previous resolution. # <--- rerere
```

Note that in this case , you will get a message saying *No files need merging* if you try to run `mergetool` as usual.
Instead, use `git add`:

```console
$ git add bar.txt
$ git diff --staged -- bar.txt # Check that the changes still make sense
$ git rebase --continue
```

If you don't like having to type `git add` explicitly, you can tell git to do it for you:

```ini
[rerere]
autoUpdate = true
```

### pull

By default, `pull` in nothing more than `git fetch` followed by `git merge`.

I usually prefer rebases over merges, so I configured `git pull` to always
perform a rebase:

```ini
[pull]
rebase = true
```

If I *really* need to merge, I'll run:

```console
$ git fetch origin
$ git merge origin/master
```

### rebase


By default, git will show you a summary of what changed (a *diffstat*) in many cases,
like a fast-forward merge:

```console
$ # on master, behind origin/master
$ git merge
Updating 24878f5..5be8c2e
Fast-forward
 bar.txt | 1 +
 1 file changed, 1 insertion(+)
```

But it will _not_ do that if you are not fast-forward and rebase a different
branch, unless you have:

```ini
[rebase]
stat = true
```

The reason may be that computing the *diffstat* is expensive (at least more
expensive than the actual merge in many cases), but personally I don't mind the cost in time.

Usually this information allow me to be aware of the potential conflicts.

#### fixing history

Let's assume you have a list of 3 commits, the last one being a fix of the
first:

```console
# edit foo.py
$ git commit -m "Foo: add bar() method"
# write some code in bar.py
$ git commit -m "Bar: add baz() method using Foo"
# realize a crash, patch foo.py again
```

Now, you want the third commit to be squashed with the first one.
This will make code review easier and a cleaner history.

There are two ways to fix this:

First, you can make a new commit and run `git rebase --interactive`:

```console
$ git commit -m "Fix Foo.bar() crash when called without arguments"
$ git rebase -i master
pick bbace84 Foo: add bar() method
pick 5499c6d Bar: add baz() method using Foo
pick 33c32e1 Fix Foo.bar() crash
# Edit file to have:
pick bbace84 Foo: add bar() method
fixup 33c32e1 Fix Foo.bar() crash
pick 5499c6d Bar: add baz() method using Foo
# quit and save
Successfully rebased and updated refs/heads/foobar.
```

Or (and this is quicker), make sure your last commit starts with
`fixup! `, followed by a prefix of the message of the commit you want to fix.

Then set:

```ini
[rebase]
autosquash = true
```

Afterwards, when you'll run `git rebase -i`, the line `fixup` will magically appear:

```console
$ git comit -m 'fixup! Foo: add bar'
$ git rebase -i master
# check the "rebase-todo" file is correct
# done!
```

### merge

```ini
[merge]
tool = kdif3
```

I use `KDiff3` mainly because I'm too used to it to change. Some facts:

* Cons:
  * It's big and slow and depends on `KDE4`
  * It makes annoying sounds (which is the cause for the huge dependency on
    `KDE4` ...)
  * It is able to solve conflicts that git does note handle automatically, which
    is nice, but sometimes this goes wrong. (it's pretty rare though)
  * It lets select you to choose 'A', 'B' or 'C' for the conflicts, but
    sometimes you want to *edit* the line directly in 'D', and the
    the editor is painful to use.
* Pros:
  * It shows you four windows: 'A', the common ancestor, 'B', the file from your
    side, 'C' the file from the other side, and 'D', the result of the merge.
  * You can use "quick&dirty" resolution methods, such as "Choose 'C' everywhere",
    or "Chosse 'C' for all unresolved conflicts"

Thus, when KDiff3 fails, I often just edit the un-merged file directly in
Neovim and deal with the conflicts markers (`<<<<<<`, `=======`, `>>>>>>`)
manually [^1].

Note: `git` automatically writes a `.orig` file during merge resolution for backup purposes.

You can turn off this feature with:

```ini
[merge]
keepBackup = false
```

It took me a while to figure this out, but KDiff3 *also* writes a `.orig` file
when it's done, so you have to untick a box in `KDiff3` settings window for the
`.orig` file to really be gone.

## Aliases

I have a *lot* of aliases. Some of them are quite common:

```ini
ci = commit
co = checkout
```

Since I never managed to remember how many *m* there are in
*amend*, I have:

```ini
mend = commit --amend
```

### Log

You'll find dozen of people trying to get a colorful and useful `git log`.

Here's my take on it:

```ini
lg = log --color --graph --pretty=format:'%Cgreen%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit
lgs = log --graph --pretty=format:'%Cgreen%h%Creset - %s %C(yellow)%d' --abbrev-commit
```

The trick is to grok the `pretty format` string. You'll find all the relevant
information in the git documentation.

### Cherry-pick

Sometimes you want to cherry-pick a bug fix from the development branch to the
release branch. In that case, adding the `-x` option causes the original sha1
not to be lost:

```console
$ git cherry-pick -x develop
$  git log
Critical bug fix

(cherry picked from commit af123ed)
```

To make sure I don't forget the `-x`, I created dedicated aliases:
```ini
ck = cherry-pick
ca = cherry-pick --abort
cx = cherry-pick -x
```


### Rebase

When you run `git rebase -i`, git will prompt you to run `git rebase --skip`, or
`--continue`. And sometimes you'll want to abort. I made it so that in any case,
I only have two letters to type:

```ini
ri = rebase -i
rc = rebase --continue
rs = rebase --skip
ra = rebase --abort
```

(Note that the alias that runs `--abort` ends with the letter `a`, like the
alias for `cherry-pick --abort`)

Usually, I'm either at work and there's a central repository at `origin`, or
I'm contributing to an open source project and I have a `upstream` origin.

So this means I need two different aliases:

```ini
ro = rebase -i origin/master
ru = rebase -i upstream/master
```

### go

`go` is `reset --hard`. It's just that almost _never_ use `git reset` without
this option, so this is more handy:

```ini
go = reset --hard
```

### @{u}

`@{u}` is a special syntax that means "the remote ref of the tracked by the
current branch'. So if you are on `master`, this usually is `origin/master`

Since `@{u}` is hard to type, I have a few aliases, all ending with `u`:

```ini
gou = reset --hard @{u}
logu = log @{u}
diffu = diff @{u}
```

For the same reason, I often need to compare with `origin/master`, so
this time the aliases end with&nbsp;`o`:

```ini
logo = log origin/master
diffo = diff origin/master
```

## Helper scripts

### As aliases
Git allows to insert small pieces of bash code instead of just a replacement
string when you start the right value with a bang:

```ini
[alias]
prune-merged = !git branch --merged | grep dm/ | grep -v "\\*" | xargs -n1 git branch -d
```

At work we all prefix our dev branches with our initials, but I often forget to
delete them when I'm done.

This alias looks for all the local branches that are fully merged and start
with `dm/` and deletes them.

Note how we use `xargs -n1` to by-pass the fact that `git branch -d` only takes
one argument.

### As standalone files

By default, when you run `git foo`, git will look for an executable anywhere in
`$PATH` named `git-foo` and run it.

(If you are wondering, the built-in commands like `fetch` or `push` are in
`/usr/lib/git-core/`)

You can combine this with aliases to get nice names for the helper scripts you
write, while still having to type fewer letters.

### Lazy push

For instance, I have:

```ini
[alias]
fp = fpush
```

And then in I have a script named `bin/git-fpush`:

```bash
#!/bin/bash

set -e

function main() {
  if [[ -z "$1" ]] ; then
    echo "Missing file name"
    return 1
  fi
  if [[ ! -f "$1" ]] ; then
    echo "$1 is not a regular file"
    return 1
  fi
  git add $1
  git commit -m "Update $1"
  git push
}

main "$@"
```

This means that when I type `git fp foo`, `git` will expand the alias to `git fpush`, and then
run the `git-fpush` script.

I use the script mostly in private repositories, when all I want is to commit
just a file, without bothering with a real message.

In the same vein, I have an other script that does everything it can to push all
the changes in just one command:


```bash
#!/bin/bash

set -e

function main() {
  if [[ -z "$1" ]] ; then
    echo "Missing commit message"
    return 1
  fi
  git commit --all --message "$1"
  git push
}

main "$@"
```

```ini
[alias]
cp = commit-and-push
```

### Rebase

Lastly I have a helper script to rebase the last 'n' commits, because,
as you could have guessed, I spent a lot of time rebasing stuff.

So `git rebase -i HEAD~5` becomes `git r 5`.

Same idea, a bash script:

```bash
#!/bin/bash

set -e

function main() {
  if [[ -z "$1" ]] ; then
    echo "Usage git r <number of commits>"
    return 1
  fi
  git rebase --interactive "HEAD~$1"
}

main "$@"
```

and an alias:

```ini
[alias]
r = rebase-n-commits
```

### Returning to the top directory

I use this command a lot. Here's the implementation:

```bash
function gcd() {
  topdir=$(git rev-parse --show-toplevel)
  if [[ $? -ne 0 ]]; then
    return 1
  fi
  cd "${topdir}/${1}"
}
```

Assuming I'm the root of the repository is `foo` and I'm in `foo/src`, `gcd` will
send me to `foo`, and `gcd include` to `foo/include`.

Note the call to `git rev-parse` which allows you to not try and duplicate the
logic used by git to find the top level directory (hint: it's harder than you
think)


## Gui tools

I do most of my git commands from a shell, but I sometimes need a graphical
interface (And use a mouse)


### gitk

I use gitk when I want to:

* Have a high-level view of the history of several branches. (Use `gitk --all`
  for that)

* Rewrite history on several branches. From gitk it's easy to checkout various
  branches, apply cherry-picks, reset branches to other commits and so on.

* Look for commits that add or remove a given string and select only the
  changes made in one given file.

  Behind the scenes, the `-S` option of `git log` is used.

By the way, `gitk` understands all the options `git log` does. So you can use:
`gitk -- src/foo` to only show the commits in a given subdirectory for instance.

### git-gui

I use git-gui when I know I left things in the files I do not want to
be part of the next commit: debug logs, comments, ...

I like the fact that you can select big hunks or small lines in a very
intuitive way.

I also use the 'revert changes made to this file' (`ctrl-j` by default) feature
a lot, because I'm looking directly at the changes that would be lost, so I feel
more confident about not overwriting something important.

Apart from that, I've added a few configuration options to have more actions
available in the top menu:

```ini
[guitool "pull-rebase"]
cmd = git pull --rebase

[guitool "clean"]
cmd = git clean -fd
confirm = true

[guitool "reset"]
cmd = git reset --hard
confirm = true
```

Note how I have `confirm = true` for the "dangerous" operations, so that
`git-gui` will display a pop-up for confirmation beforehand.

The last one is to activate spell checking for English when writing the commit
message:

```ini
[gui]
spellingdictionary = en_US
```

I have a similar configuration for Neovim:

```vim
augroup spell
  autocmd!
  autocmd filetype gitcommit  :setlocal spell spelllang=en
augroup end
```


## Neovim

The last piece of the puzzle is the interaction with Neovim.

I use Tim Pope's [vim-fugitive](https://github.com/tpope/vim-fugitive) for this.

It has *tons* of features.

I use it to display a current branch in my status line:

```vim
set statusline=%{VimBuddy()}\ [%n]\ %<%f\ %{fugitive#statusline()}%h%m%r%=%-14.(%l,%c%V%)\ %P\ %a
```

Yup, you can configure your status line by just setting a variable, no need
for dedicated plugins&nbsp;&hellip;[^2]

Note that most of the commands only work if fugitive detects that you are
editing a file from a git repository.

Here are the commands I use the most, followed by the effect they have
assuming I'm editing a file named `foo.c`:


* `:Gwrite` run `git add foo.c`
* `:Gread`: restore contents of `foo.c` from the latest commit (aka: undo all
  unstaged changes)
* `:Gmove foo2.c`: run `git mv foo.c foo2.c`, and switch to `foo2.c` buffer without
  telling you "foo.c is no longer available") [^3]
* `:Gdiff`: show the differences made in `foo.c`. By default, the starting point
  is the current branch, but you can use `:Gdiff origin/master` to select a
  different starting point for instance.
* `:Gblame`: run `git blame foo.c`, and when pressing 'Enter' when the cursor
  is at the end of line, show the details of the matching commit.
* `:Ggrep`: same as `:grep`, but use the built-in `git grep` command. Since
  there are (rare) occasions when I'm _not_ in a git repository, I tend to use [Ag.vim](
  https://github.com/rking/ag.vim) too.
* `:Gcd`: exactly the same effect as the `gcd` command described earlier :)

# Conclusion

git takes quite some time to learn, but also offers tons of way to customize
its behavior.

I hope I've given you an idea of everything that is possible.

Until next time!


[^1]: I tried to use Neovim directly as a git mergetool, but I find it too much confusing.
[^2]: The `VimBuddy()` part can be seen in action [on asciinema](https://asciinema.org/a/47001)
[^3]: By the way, the ':Move' command from Tim Pope's [vim-eunuch](https://github.com/tpope/vim-eunuch) does the same thing.
