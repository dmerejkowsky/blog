---
authors: [dmerej]
slug: rewriting-z-from-scratch-part-2
date: 2017-06-10T11:39:51.948731+00:00
draft: false
title: Rewriting z from scratch, part 2
tags: ['python', 'zsh']
---

[Last month]({{< ref "/post/0041-rewriting-z-from-scratch.md" >}}) I
wrote about how I rewrote `z` from scratch after I started using `fzf`.

10 days later I posted the following [toot](https://mamot.fr/@dmerej/1825106) on Mastodon:

> There's a problem with my implementation: 'recent' paths only get priority
> after they've been accessed enough times.
>
> There's an elegant solution for this, let's see if you can find it!
>
> There's a clue on my github repo:
> https://github.com/dmerejkowsky/dotfiles/branches
>
> Answer on my blog soon.
>
> PS: No spoil, please

Well, it's time for me to give the answer.


<!--more-->

# Following the clues

You can skip this part if you don't care, or if you want to look for the answer
yourself.

The clue on my github repo was this [pull request](
https://github.com/dmerejkowsky/dotfiles/pull/3).

The branch is called `cwd-history-squared`.
There are two commits.

The first is:
```text
Revert "cwd-history: now backed by a json file"

This reverts commit 96a9080.
```

The second is just a fix because the revert broke the `clean` command.

I left this comment:

```text
This reverts commit 96a9080.
There's more to it of course.
Can you guess what's next?
Surely I must have pushed the rest of the commits some place else ...
```


So where are the rests of the commits?

The trick was to go visit the page at
[https://dmerej.info](https://dmerej.info). It's displayed pretty much on all
my public profiles (github, twitter ...).

From there, you can find a link to a [git repository browser](https://dmerej.info/git/) which
contains a [mirror](https://dmerej.info/git/dotfiles/) of my dotfiles repo.

The description says:

```text
Mirror (almost) of github.com/dmerejkowsky/dotfiles.git
```

And if you look for the [cwd-history-squared](
https://dmerej.info/git/dotfiles/log/?h=cwd-history-squared) branch, you find the missing
[commit](https://dmerej.info/git/dotfiles/commit/?h=cwd-history-squared&id=5c10af223386b182d487ede21f8bf07ab11cedaf):

```text
cwd-history: store paths chronologically with no duplicates
```

And that's how you were supposed to find the answer.

By the way here's the reason the branch is called `cwd-history-squared`: the
tool itself is called `cwd-history`, and the paths are stalled
*chronologically*, following the *history* of my navigation across directories.

I never got any feedback on this little puzzle, though :/ Maybe no one even tried, or
maybe the puzzle was too hard, I don't know. Feel free to [tell me about it](
{{< ref "/pages/contact.md" >}}) though :)

Anyway, now the commit has been [merged](
https://github.com/dmerejkowsky/dotfiles/commit/0d5780c87dab3093266357663736d23296ca8b62),
so the answer maybe a bit easier to find.

I still have a few things to say about the commit itself, so let's dive into it.

# Order, please!

In the previous version, paths were stored in a `json` file used as a database.
The database would track the number of times each path was visited, so that most
used paths would get displayed first.

After using this implementation for a while, I found have the following
workflow when I start working on something new:

* Go to a folder `cd ~/work/stuff`
* Open `vim`
* Need to run a command while keeping the editor open
* Open a new terminal [^1]
* Run `z stuff` and scroll because there's already paths matching
  'stuff' in the `cwd-history` database.

This was really annoying, so I decided to try something new.

Here's the relevant part of the new version of the code:

```python
def add_to_db(path):
    paths = read_db()
    if path in paths:
        paths.remove(path)
    paths.append(path)
    write_db(paths)
```

Basically we make sure that latest paths are always appended at the bottom of
the list, while making sure there are no duplicates.

Thus, the last part of the workflow is now:

* Type `z` without argument
* Type `enter` to select the element at the bottom (fzf starts with the cursor
  at the bottom of the list by default)
* Type `enter` to enter the lastly visited directory

I can tell you the `z-enter-enter` sequence took no time to become part of my
muscle memory, which is a great sign that I found something that works well :)

I also really like that the implementation is simpler and easier to explain, so
it might be a good idea [^2].

That's all for today, see you next time.

PS: I lost [the game](https://en.wikipedia.org/wiki/The_Game_(mind_game))...


[^1]: Yeah, I know that it's easy to configure a shortcut so that you can open a second terminal from the first one while keeping the working directory. I even [wrote a patch](http://bazaar.launchpad.net/~yannick-lm/sakura/new_window/revision/310) for this back when I was using sakura. But still, sometimes you want to re-use an existing terminal.
[^2]: Congrats if you recognized the [zen of Python](https://www.python.org/dev/peps/pep-0020/)
