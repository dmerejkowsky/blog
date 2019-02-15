---
authors: [dmerej]
slug: tips-from-a-build-farmer-part-1-ci-scripts-are-scary
date: 2018-08-20T10:35:17.547719+00:00
draft: false
title: "Tips From a Build Farmer - Part 1: CI scripts are scary"
tags: [ci]
summary: The ugly truth about CI
---


_Note: This is part 1 of the [Tips From a Build Farmer]({{< ref "/post/0082-introducing-tips-from-a-build-farmer.md" >}}) series._


Here's an simple yet somewhat realistic CI script, in Bash:

```bash
echo "fetching latest changes"
git fetch
git reset --hard @{u}
echo "compiling" ...
make
echo "running tests" ...
make test
echo "generating archive" ...
DESTDIR=/tmp/foo make install
cd /tmp
tar cvfz foo.tar.gz foo
```

This code fetches the latest changes, compile the code, runs the tests and finally generates an archive.

What's so scary about those few lines? Isn't this just *boring*?

Well, let's have a look, and note that everything I'm about to tell you is  **based on true stories.** [^1]

One last thing before we start: let's assume it takes 5 minutes to compile the code, and 10 minutes to run the tests.


# The Slow Development Trap


Right before your fist public release, you discover that the archive does not contain any README. You then add a single line of code to copy the README file from the sources to the directory used to generate the archive:

```patch
  ...
  echo "generating archive" ...
  DESTDIR=/tmp/foo make install
+ cp README /tmp/foo
  cd /tmp
  tar cvfz foo.tar.gz foo
```

Then, to see if your code is working, you have to *wait the duration of the entire build* before knowing if your code is correct.

So you wait 20 minutes, and the CI script dies right before generating the archive:

```
fetching latest changes
compiling ...
runinng tests ...
generting archive ...
cp: cannot stat 'README': No such file or directory
```

Oops, turned out the README was called `README.md` and not just `README`.

So you make an other change:

```patch
- cp README /tmp/foo
+ cp README.md /tmp/foo
```

You wait an other 20 minutes, and the build passes again.

Congrats, you just *spent 40 minutes making a one-line patch (!)*.

That's what I call "The Slow Development Trap".

But wait, it gets worse.

Let's keep our simplistic example and study a few bugs you may encounter.

# CI bugs and where to find them

## The fatal typo

![All the automated tests have crashed - it's normal](/pics/geek-and-poke-its-normal.png)


First example: the script always crashes right before running any test:



```bash
echo "compiling" ...
make
echo "running tests" ...
make tests
...
```

```
make: *** No rule to make target 'tests'.  Stop.
```

Got it? The Makefile target is called `test`, singular, not `tests`, plural.

If you're lucky, your team mates will wait until you fix the problem, but some may be entitled to by-pass CI completely because "we have run all the tests on our machines before running `git push` like we always do".

Hint: they didn't. No one ever does that *all the time*, and it's the very reason we use CI in the first place. So better hurry before the master branch is full of failing tests. And remember the Slow Development Trap.


# Forgetting something important

Second example:

```bash
echo "fetching latest changes"
git reset --hard @{u}
echo "compiling" ...
make
echo "running tests" ...
make test
```


Your forgot to call `git fetch`. The logs look like the code was updated, but in reality you just keep resetting the working tree to the same commit.
Since this was a good commit, all the tests always pass.


A week later you find several bugs have been introduced because the developers wrongly assumed the tests were run on the version of the code they just pushed (and who could blame them?). Also, it's going to take quite some time before the team starts trusting the CI scripts again. [^2]

# Un seul être vous manque ...

Third example: You are building a Qt application and in the Makefile you use to install, the rule to copy `libQt5Widgets.so` is missing.

The main program then crashes horribly the first time it is run right after installation.

```
error while loading shared libraries: libQt5Widgets.so.5:
cannot open shared object file: No such file or directory
```

This means that you can no longer ship, you can no longer do QA, and everyone gets stuck until you fix the bug (and we're back to 'development is slow')

By now you should have realized that **you are not allowed to have bugs in your CI scripts**.

Scared much? Let's talk about time travel for a change.

# Back to the future

Your team is working on a brand new product they intent to release in two months. You start writing CI scripts right away. But you still have to travel to the future and make sure the scripts you wrote today still work. Or at least, you can make them work quickly. Remember: "no bugs allowed".

So, in addition to not be allowed to have any bugs, you *also* have to **implement all the required features** and you **cannot miss the deadline**. If you're late, you can't ship. Or worse, you'll ship by doing the required steps by hand, and then you'll get an whole new set of problems.

# Forward from the past

Two years ago you released version 2.5.2 of your flagship product, the last of the 2.x series.

Since then you made some pretty big redesigns, and released version 3.0 and 3.1. Most of your clients have made the switch, developers are happy to no longer have to work on the ancient code base, everything looks OK.

But then someone sends you an e-mail saying they've found a security bug in the 2.5.2 release, and they will disclose it next week no matter what.

Your team spends 1 day discussing and planning a fix. Then they take 3 days to actually implement it, because they have to find their way in an old code base no-one no longer knows very well.  Now it's time to QA the 2.5.3 release.

Better be sure the scripts you wrote two years ago still work, or everyone will be getting a very hard time!

OK, enough with scary stories, let's talk about the craft of writing CI code. I'm afraid I have some bad news there too.

# Your standard approach will not work

![my normal approach is useless here](/pics/xkcd-normal-approach.jpg)

Writing CI scripts is very different than writing production code or test code. It's a whole different world. Let me elaborate.

## Testing is hard

Writing automated tests for CI scripts is difficult and almost never catch any bugs (at least, based on my experience). The best way to check that a CI script works is by running it it its entirety. And then you fall yet again into the Slow Development Trap.

## Debug is hard

CI scripts are hard to debug because they usually don't run on developer's machine but on runners where debug tools are seldom found.

If the worst case scenario (which happens quite often), your only option will be to add debug logs and this means getting caught by The Slow Development Trap all over again.


# Eliminating fear

By now you should start getting nervous.

TDD helped *me* getting rid of the fear of changing production code by teaching me a way of writing tests and production code in a nice loop that often leads to code that has a high quality and few defects.

For this series, I will be trying to do the same thing. I'll tell you how to resist the Slow Development Trap, and how to avoid the bugs we discussed (and many others). Hopefully next time you'll have to change a CI script it will be less scary.

See you next time, where we'll introduce a few useful concepts.

[^1]: I'm not going to give you proofs of these events because they're quite embarrassing for everyone involved.
[^2]: That happened to me by the way: *I* was the guy who forgot to fetch.
