+++
slug = "why-i-love-arch-linux"
date = "2016-06-28T21:13:29+02:00"
description = ""
draft = false
title = "Why I Love Arch Linux"
+++

I've started using Linux in 2005 with Ubuntu.

After that, I've tried and use a few other distributions, such as Debian,
Fedora, Gentoo, Frugalware for a few years until I found Arch Linux around 2008.

Since then I've sticked with Arch Linux. Here's a post explaining why.
(If you like it, there may be more posts on Arch Linux later ...)

<!--more-->

# Context

I'm going to use a post I've seen on the Arch Linux forums.

Some time ago, there was someone complaining that one of the packages he was
using was not up-to-date, and was asking when there will be an update.

He got the usual response:

* Arch developers don't read the forums
* The package will be updated "when it's ready"

And then one of the moderators moved the entire thread to "Topics Going Nowhere"
(It's a section of the forum which is only available to subscribed members: the idea
is to keep some of those posts out of search engines)


Discussion continued, and the OP said:

> While I understand that post is supposed to be there to stop people from
> asking the same questions over and over again, but to be honest I find the
> answer sound quite arrogant and unhelpful. "When it's ready" is not an
> answer, all it communicates is that "you are not allowed to ask this
> question" which is a totally inappropriate message from an open source
> project that is supposed to be all about community and openness.

# The moderator's answer

That's where the story gets interesting: the moderator replied:


> Actually, it is an answer and, no, you are not encouraged to ask the question.
> For two reasons:
>
> One, this is a rolling release project, if every time someone thought that it
> would be a good idea to ask when $package was ready, the boards/IRC/ML would
> be full of the same. stupid. question.
>
> Two. This is Arch. If you want the newest release, don't ask when it will be
> ready; grab the PKGBUILD and update and install it. Problem solved.
>
> If neither of those reasons is sufficiently clear, or you can't accept them,
> you are using the wrong distribution.

# What I like about Arch

That's what I like about this distribution:

* It's a rolling release, so you never have to use outdated software: packages are
  available usually rather soon after their upstream release, and even when they
  don't, it's easy to update the `PKGBUILD` yourself, for two reasons:
  * 1/ The syntax of the `PKGBUILD` is one of the easiest I know to describe how a package
    should be built.
  * 2/ New versions of software tend to depend on the last stable version of their dependencies,
    which is OK when using Arch: when a new version of a library is out, Arch
    promptly updates it and rebuilds all the affected packages, without caring
    of keeping the old version in place (well, except for huge libraries like `Qt4` and
    `Qt5`&nbsp;...)

* The OP said the response was "arrogant" and "unhelpful". It's not. <br/>
  As said in the [Arch Linux Wiki](https://wiki.archlinux.org/index.php/Arch_Linux#Principles),
  It's just that this distribution is targeted at the "proficient Linux user".
  It's not a "user-friendly" distribution, it's a "user-centric" distribution, which means
  the goal is _not_ to have as many users as possible, but to put the _competent_ user
  in control.

# Conclusion

So, in summary I'm very careful when I suggest someone to try Arch Linux: you've got
to be willing to spend time reading documentation and configuring things, since
the distribution will not "hold your hand" and do it for you. You'll also have
to carefully read the news and sometimes perform a "required manual intervention" ...

On the other hand, if you're eager to learn more about how a Linux system works, give it a try!
The other options are Gentoo, or Linux From Scratch, but life is too short to
spend your days watching code compiling ...
