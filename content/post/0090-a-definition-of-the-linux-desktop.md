---
authors: [dmerej]
slug: a-definition-of-the-linux-desktop
date: 2018-12-31T15:58:07.228445+00:00
draft: true
title: "A definition of the linux desktop"
tags: [linux]
---

# Introduction

Quite some time ago, I came across a thread from Gary Bernhardt on twitter.

Here's what he had to say about Linux, compared to macOS and Windows:

> Unlike the other two operating systems, you have control. But nothing will ever
> work reliably, especially across upgrades. When it breaks, the community will
> frame it as your own moral failure.

As a guy who uses Linux for almost everything (both at work and at home), you may think I would disagree.

But no, I agree with almost everything, except I would rephrase the last sentence. Let me explain.

# Control

Let's start at the beginning. What *control* do you have?

## Control on macOS

You have almost no control over hardware. You buy hardware that is manufactured by Apple, often in an "Apple store".

Most applications have minimal configuration, simple things like preventing the laptop to suspend when closing the lid are hard to achieve [^1]

Finally, you often haven little control over *your own data*. Watching the movie you bought on iTunes on an non-Apple device is very hard.

You can put all your stuff on iTunes or iCloud, but if you loose access to your account you lose everything. [^2]

## Control on Windows

Compared to macOS, you hae more control over hardware. For instance you do not need to buy an (expensive) control chord everytime you upgrade your laptop. You can buy a new battery when the one you use is failing, and so on.

But still, you  less and less control over what to update and when, and let's not talk about privacy...

## Control on Linux

You control (almost) everything.

You can choose your distribution. You can choose its "stability". For instance on Debian, you can choose between "old stable", "stable", "unstable", "testing" and "sid".

You can chose your desktop environment: KDE, Gnome, LXDE, XFCE, Mint, or even use no desktop environment at all.

You can can choose your window manager, your init system, your package manager ...

You can choose when and what to update (less so on "rolling distros" lie Arch Linux, although it is still possible with extra care ...), etc.

Control is everywhere and so ubiquitous it's even scary. But it's free: both as free beer *and* free speech, so nothing prevents you from experimenting but time and energy.


# When it breaks

Let's talk about what happen when software you are using breaks.

On macOS and Windows, all you can do is pray and find someone who has a solution. There are bug trackers of course (but on macOS you can only see the bugs *you* opened).

If you upgrade Windows and a third-party driver stops working, you're basically screwed. I've seen my Mom loose access to its scanner for a few months because of this.

On Linux, things *will* break more often. They are less people to do QA, there are more unknowns, tons of different configurations (as we saw in the "control" section), and a pressure to release often and stay "bleeding edge".

Almost everything is written and maintained by non-paid volunteers.

Upgrades are big and scary, and so stuff breaks more often. No point discussing that.

Hell, right now on my laptop the brightness control does not work and it used to work fine when I bought it.

By the way, I did not take the time to look for a solution, which leads us to the next section.

# Your own moral failure

Let's take a look at some exchanges between an average user with a problem, looking for answer from the community, for instance in a public bug tracker or a forum.


> Q: I've upgraded foo to version 3.0 and now I can frob anymore <br />
> A: Did you read the changelog *before* upgrading?

<span/>

> Q: I bought a new printer and I can only print in black and white! </br>
> A: Did you research compatibility with Linux before buying the new printer?

Let's try to put ourselves in the shoes of this user. He or she might thing it failed at something, or even that he's not even supposed to ask this kind of question[^3], which illustrates with the "moral failure" Gary talked about.

# Rephrasing the last part

So where do I disagree? Well, it's the "framing" part I don't like. I would rephrase the last sentence as: "When it breaks, it will be your (or the community's) responsibility to fix it".

Let me elaborate.

When stuff on Linux breaks, you *can* do something about it.

You can downgrade, you can switch to an other distribution, you can discuss the problem on a forum, you can send e-mails to mailing list, you can open an issue on the bug tracker.

You can even get the code and patch it yourself if you are not afraid. Sometimes it's not that hard.

So I don't think the community is *framing* it. I just think it's how things work in the Linux world. You just can't expect volunteers to always fix all the bugs for free. And you can't expect the same level of quality as when QA is done by paid professionals.

So, yes, in exchange for the freedom of control you get some duties. Your duty is to help yourself and others when things break. And by the way, teaching users about reading changelogs and doing research before buying hardware is good advice, *if* they are willing to accept it.

For me those duties are a small price to pay because I value control and freedom more than convenience.

If you are willing to accept those duties to gain this freedom and are not using Linux, give it a go!

If you are using Linux and want to "convert" other people, (like friends or family), explain this to them so they don't get mad at you.

Be ready to help them for things they don't understand. You can even teach them a few things, or teach them how to learn. That's how I got to use Linux in the first place almost 15 years ago.

And if you don't want to try and fix stuff when it breaks, keep using macOS or Windows. There's nothing wrong with that.

Cheers!

[^1]: I spent a day looking for a solution, then decided I did not really needed it. But if you know how to do it, please let met know :)
[^2]: Ask [duckduckgo](https://duckduckgo.com/?q=itunes+update+data+loss&t=h_&ia=web) if you think it's a rare problem ...
[^3]: This is not hypothetical. I've talked about that in an article called ["Why I love Arch Linux"]({{< ref "0013-why-i-love-arch-linux.md" >}})
