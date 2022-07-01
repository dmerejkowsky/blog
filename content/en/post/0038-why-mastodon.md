---
authors: [dmerej]
slug: why-mastodon
date: "2017-05-01T11:16:14.779697+00:00"
draft: false
title: Why Mastodon
---

On April 20th 2017, I created my first [Mastodon](https://mastodon.social/about) account,
`@dmerej@mamot.fr`.

In this article, I'd like to show you why this matters a great deal to me,
using three articles I've already written:

* [Heard and Seen at FOSDEM 2017](
  {{< ref "/post/0034-heard-and-seen-at-fosdem-2017.md" >}})
* [Twitter and me, me and twitter](
  {{< ref "/post/0032-twitter-and-me-me-and-twitter.md" >}})
* [How to build decentralized social networks](
  {{< ref "/post/0029-how-to-build-decentralized-social-networks.md" >}})

<!--more-->

## Previously, on this blog

### Heard and seen at FOSDEM 2017

When I was at FOSDEM in February, I spent a lot of time in a room called
"Decentralized Internet".

I heard about many nice projects and people - all of them shared the
same concern for their users' privacy, and all of them wanted to avoid
having all their data centralized in one place.

They were trying to fix the same problems, but each of them with a different
approach.

There was not a single way of doing things, (except of course using open source
software), not a single set of tools, not a single protocol, even though people
were trying to share ideas and code.

But that was kind of the point, right? If you want to build a "decentralized"
Internet, you'll like the fact there are lots of alternatives and choices.


### Twitter and me, me and twitter

Here I explained that when twitter did not have that many users, it was a much
nicer place to hang out and share experiences.

I also said that by following too many people, I ended up spending a lot
of time and energy going through my timeline, and how I "fixed" this by making
sure I would never follow more that 20 people on twitter.

### How to build decentralized social networks

Lastly, I said that for all these reasons, I had an idea for a twitter
alternative, and I enumerated two key features:

* Easy to deploy
* A maximum number of people per instance.


## Here comes Mastodon

And then I heard about the Mastodon project.

As you would have guessed, some characteristics of the project match what I
was talking about on my blog.

### Easy to deploy

There is already quite a lot of [documentation](
https://github.com/tootsuite/documentation#running-mastodon) on the subject.

Among other things, you can use Heroku or Docker to quickly and simply deploy
your own instance.

It seems to work well, given the [list of instances](https://instances.mastodon.xyz/list)
that are already available.

### The big bazaar at work

Mastodon is an alternative to an existing project, [GNU Social](https://gnu.io/),
which itself was a continuation of the
[StatusNet](https://www.softaculous.com/apps/microblogs/StatusNet) project.

For me it's just an other example of the "Cathedral and the
Bazaar" phenomenon[^1]. Instead of having a few people trying to design something
monolithic and centralized, Mastodon kind of emerged from a big "bazaar" of
people and solutions with no discernible leaders of central authority, which
what exactly what I was expecting after going to FOSDEM 2017.

### Small instances

As soon as Mastodon starting to become "popular", it was no longer possible to
create an account on the main instance, *mastodon.social*, so naturally people
started creating and using new instances.

Here's the "maximum number of users" feature I was talking about. True, it's not
hard-coded in Mastodon's source code, but because instances are usually
installed and maintained for free by small communities with few financial
resources, most of them naturally refuse to host too many accounts.

## Conclusion

I encourage you to give Mastodon a try. After you've chosen your instance, using
the website is not very difficult if you already know how to use Twitter.

You can use [mastodon-bridge](http://mastodon-bridge.herokuapp.com/) or the
search bar at the top left to find friends.

There are also some nice features:

* The 500 characters limit makes it easier to have meaningful conversation.

* There's no algorithm building a "You might like" list. Instead, you can see
  everything that happens in you "local timeline", which fosters serendipity and
  avoids the [Filter Bubble](https://en.wikipedia.org/wiki/Filter_bubble)
  effect.

Lastly, it may be the first truly "social" website, as Lionel Dricot pointed out
on [his blog](https://ploum.net/mastodon-le-premier-reseau-social-veritablement-social/)
(in French).

I'll leave you with one last quote, a translation of a tweet from a friend:

> Changing the world is hard. Some people more clever and active than me are
> already on it.

[^1]: Here's the [wikipedia article](https://en.wikipedia.org/wiki/The_Cathedral_and_the_Bazaar) if you've never heard about it.
