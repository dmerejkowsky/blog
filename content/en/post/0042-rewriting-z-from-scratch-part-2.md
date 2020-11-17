---
authors: [dmerej]
slug: rewriting-z-from-scratch-part-2
date: "2017-06-10T11:39:51.948731+00:00"
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
<!--more-->

Well, now it's time to dig into the answer to this question.

# Order, please!

In the previous version, paths were stored in a `json` file used as a database.
The database would track the number of times each path was visited, so that most
used paths would get displayed first.

After using this implementation for a while, I found I had the following
workflow when I started working on something new in a new directory, but
which name already partially matched previous entries.

* Go to a new folder `cd ~/work/stuff`
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

[^1]: Yeah, I know that it's easy to configure a shortcut so that you can open a second terminal from the first one while keeping the working directory. I even [wrote a patch](http://bazaar.launchpad.net/~yannick-lm/sakura/new_window/revision/310) for this back when I was using sakura. But still, sometimes you want to re-use an existing terminal.
[^2]: Congrats if you recognized the [zen of Python](https://www.python.org/dev/peps/pep-0020/)
