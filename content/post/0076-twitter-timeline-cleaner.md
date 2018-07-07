---
authors: [dmerej]
slug: twitter-timeline-cleaner
date: 2018-07-07T13:13:13.346483+00:00
draft: false
title: "Twitter Timeline Cleaner"
tags: [ideas]
summary: |
  What if you could spend less time on twitter trying
  to keep up with tons of stuff you don't really care about ?
---

_Note: this the second post in the [Quantum of Ideas]({{< ref "post/0057-introducing-quantom-of-ideas.md" >}}) series._

# Introduction

I've already explained [on this blog]({{< ref "post/0032-twitter-and-me-me-and-twitter.md#fixing-my-timeline" >}}) why I've decided to never follow more than 30 accounts on twitter.

To this day, I'm still convinced that if you follow more than 50 accounts, you should seriously considering cleaning your timeline too.

This may seem like a daunting task, especially if you're already following hundreds of accounts. That's when the Twitter Timeline Cleaner comes in.

# How it works

_Remember, this is **not** an existing product, just a "work in progress" idea._

* First, the TTC does a backup of the list of all your followers

* Then it goes through the list, and for all of account you follow, it:

  * Takes a random sample of recent tweets from this account and asks you to mark them as *relevant* or *useless*.
  * Then it gives each account a score, something like the average interest of each tweet divided by the frequency of tweets.

  That way, accounts that tweet rarely but are always interesting get a high score. Accounts that tweet several times per day every day, even if they sometimes have interesting content, get penalized.

When this is done, the TTC shows you a list of accounts sorted by decreasing score, and all you have to do is to select which irrelevant accounts you want to stop following.

By the way, unless they explicitly configured their account to do so, each account you unfollow will *not* get notified, so there's a pretty good chance they won't get mad at you.


# Conclusion

And that's all there is to it. We could also extend the TTC so that it prevents *you* from becoming an account with low signal-to-noise ratio using the same technique. For instance, it would display messages like: "only 2% of readers found this tweet interesting", or "you've already tweeted 3 times today, maybe go take a break".


&hellip; or you could just [use Mastodon]({{< ref "post/0038-why-mastodon.md" >}}) where:

* you can choose an instance that matches your interests
* messages are more likely to get interesting due to the 500 characters limit
* discussions are easier to follow because everything is sorted by chronological order
* people are just overall nicer to each other or so it seems


Cheers!
