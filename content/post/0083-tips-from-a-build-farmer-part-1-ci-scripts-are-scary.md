---
authors: [dmerej]
slug: tips-from-a-build-farmer-part-1-ci-scripts-are-scary
date: 2018-08-20T10:35:17.547719+00:00
draft: true
title: "Tips From a Build Farmer - Part 1: CI scripts are scary"
tags: [ci]
summary: The ugly truth about CI
---


_Note: This is part 1 of the [Tips From a Build Farmer]({{< ref "post/0082-introducing-tips-from-a-build-farmer.md" >}}) series._

Staying that CI scripts are scary may sounds weird to you.

I can hear you say: "all I need to do is write a script that calls `make && make test` and I'm done, right?".


Wrong. Here are a few examples of what could go wrong.

Note that all these examples are **based on true stories.** [^1]

# Development is slow

Let's take an example. Your have a script that builds everything, then run the tests, and then generates a final delivery, like a `.tar.gz` archive.

Let's assume you discover that the archive does not contain the README.md file found at the root of your repository.

So you ad a single line of code to the CI script that copies the README.md file in the directory used to generate the archive.

But, to see if your code is working, you'll have to *wait* entire build before knowing if you line works.

This gets old very fast, especially when you discover that the README is actually called `README.txt` and not `README.md` and have to again wait a long time before checking if your fix works.


# No bugs allowed

Let's say you have a script that should fetch the code, then build it and run the tests, and let's look at a few ways things may go terribly wrong.

First example: the script always crashes right before running any test. If you're lucky, your team mates will wait until you fix the crash, but some may be entitled to by-pass CI completely because "we have run all the tests on our machines before running `git push` like we always do". Hint: they didn't. No-one ever does that *all the time*, and it's the very reason we use CI in the first place.

Second example: your code actually never fetches. So all the builds actually use the same state of the source code, and the tests always pass because that particular commit was a pretty good one.

A week later you find several bugs have been introduced because the developers wrongly assumed the tests were run on the version of the code they just pushed (and who could blame them?). Also, it's going to take quite some time before the team starts trusting the CI scripts again. [^2]

Last one: you are building a Qt application and for some reason `libQt5Widgets.so` is missing and thus the program crashes horribly right after installation.

This means: that you can no longer ship, you can no longer do QA, and everyone gets stuck until you fix the bug (and we're back to 'development is slow')

# Time travel

## Back to the future

Your team is working on a brand new product they intent to release in two months. You start writing CI scripts right away. But you still have to travel to the future and make sure the scripts you wrote toda still work. Or at least, you can make them work quickly. Remember the "no bugs allowed" part.

## Forward from the past

Two years ago you released version 2.5.2 of your flagship product, the last of the 2.x series.

Since then you made some pretty big redesigns, and released version 3.0 and 3.1. Most of your clients have made the switch, developers are happy to no longer have to work on the ancient code base, everything looks OK.

But then someone sends you an-email saying they've found a security bug in the 2.5.2 release, and they will disclose it next week no matter what.

Your team spends 1 day discussing and planning a fix. Then they take 3 days to actually implement it, because the have to find their way in an old code base no-one no longer knows very well.  Now it's time to QA the 2.5,3 release. Better be sure the scripts you wrote two years ago still work, or everyone will be getting a very hard time.

# Your standard approach will not work

Writing CI scripts is very different than writing production code or test code. It's a whole different world.

## Debug is hard

CI scripts are hard to debug because they usually don't run on developer's machine but on runners where debug tools are seldom found.

If the worst case scenario (which happens quite often), your only option will be to add debug logs, but that means paying the cost of waiting for the build even higher.


## Testing is hard

Writing automated tests for CI scripts is difficult and almost never catch any bugs. At least, based on my experience. The best way to check a CI script works is by running it it its entirety. This again leads to our "development is slow" item.


# Eliminating fear

By now you should start getting nervous. <small>(I'm even getting nervous myself while writing this)</small>.

TDD helped *me* to get rid of the fear of changing production code by teaching me a way of writing tests and production code in a nice loop that always leads to code that has a high quality and few defects.

For this series, I will be trying to do the same thing: share my experience and some tips to help you eliminate the fear caused by all these nasty facts we discussed.

See you next time, where we'll answer the number 1 question: "which programming language should I use?".

[^1]: I'm not going to give you proofs of these events because they're quite embarrassing for everyone involved.
[^2]: That happened to me by the way: *I* was the guy who forgot to fetch.
