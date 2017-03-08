---
slug: how-to-build-decentralized-social-networks-part-2
date: 2017-03-08T21:24:01.045553+00:00
draft: true
title: How to build decentralized social networks, part 2
---

Back in January 2017, I wrote a post called:
*[How to build decentralized social networks](
{{< relref "2017-01-06-how-to-build-decentralized-social-networks.md" >}})*

In it, I briefly introduced a project called `ynxice`, a twitter clone
with a hard-coded limit of users.

The post ended with a cliffhanger, saying that I would write a follow-up
in February.

Well, I'm late, but "Better late than never", right?

Here's what happened since I wrote this post.

<!--more-->

## The Room at FOSDEM

I went to [FOSDEM](
{{< relref "2017-02-11-heard-and-seen-at-fosdem-2017.md" >}}) and spent almost
the whole day in the "Decentralized Internet" dev room.

I learnt about tons of nice projects, and added quite a few URLs in the
[links page]({{< relref "pages/links.md#decentralized-internet" >}})[^1]

## Progress on the ynxice project

I'm sorry to say I have absolutely *zero* code to show you.

Initially, I wanted the project to be _really_ easy to deploy so I thought about
using `Go` for the server.

But between `yunohost`, `libre.sh`, or `puffin`, or `ansible`, deploying will probably
not be an issue, there's already many good solutions to choose from. (Thank you,
open-source !)

So I started playing around with `django`, but for now I'm not really sure how to
handle authentication. (This stuff is _hard_)

In the process I learned a few things about ORMs, and I've though more about the
hard-code limit on the number of users and what it means.

So stay tuned for more, the story is just beginning ...

See you later!


[^1]: By the way, if you have interesting links to contribute, please [leave a comment]({{< relref "pages/links.md#comments" >}})
