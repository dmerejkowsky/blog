---
authors: [dmerej]
slug: its-not-a-waste-of-time
date: 2020-05-30T10:18:46.601899+00:00
draft: false
title: "\"It's a waste of time!\""
tags: [misc]
summary: Stop saying that if you're not sure.
---

I have a confession to make : every time I heard the phrase "It's a waste of time!", I get a little angry.

I've heard this answer countless times, often after suggestions like:

* "Let's write tests before writing production code"
* "Let's write documentation before writing code"
* "Let's refactor before implementing the new feature"
* "Let's discuss the API once more before shipping the next release."

There are several reasons for why I don't like this answer.

Why? It's all about knowledge.

# Time spent vs time saved

First, it's easy to see the time _spent_.

Yes, we spent one week writing and reviewing the new documentation. Yes, we spent three days refactoring the code and we did not implement any feature. Yes, we had two one-hour meetings before getting consensus on the new API and shipping the next release.

But it's really hard to see the time _saved_.

Who knows what horrible bug we would have to fix in production if we skipped writing those tests? Who knows how much breaking changes we would have made because the API was not good enough? Who knows how much time we would have spent implementing the *next* big feature if we skipped the refactoring?

# Learning about the problem

Second, you may have noticed that in all the situations I mentioned above, it's all about gaining more knowledge about the problem _before_ jumping to the implementation.

In other terms, by saying "It's a waste of time", you assume you know enough about the problem to start working on the implementation right away.

# Trying to convince others

Most of the time, I can't convince people who tell me that I'm suggesting is a waste of time.

Instead, they skip what I think was a critical preparatory step, and then I watch them spend a ton of time rectifying the situation afterwards - it's frustrating.


Fortunately, after they've repeated the same mistake enough times, they tend to finally listen to me. But I'd very much like to not have to go through this painful process every time.

I'm not sure what to do about it, though. Maybe it's just human nature?

To make matters worse sometimes writing the code is actually a good way to gain this precious knowledge in a way that neither tests nor documentation nor brainstorms could have done.

# Questions for you

What do you think about all this? How do you react when confronted to the "It' a waste of time!" argument?

Feel free to share your ideas below, and see you next time!

