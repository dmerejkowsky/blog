---
slug: twitter-and-me-me-and-twitter
date: 2017-01-28T16:02:39.020363+00:00
draft: false
title: Twitter and me, me and twitter
---

Some time ago, I pinned the following tweet on top of my timeline:

> Announce: I've decided to no longer follow more than 20 people.
> Maybe one day I'll explain why on my blog.
> (Not sure yet)

Well, it's time to explain myself, and, as often on this blog, the post will
start with a story.

<!--more-->

## First days

I spent a lot of time on twitter without any account. I just used to open
various timelines of people I'd like.

Doing so was just a matter of opening `https://twitter.com/<handle>` and
scrolling to get latest messages, or when I had time,
`https://twitter.com/<handle>/with_replies`, especially when I was enjoying
someone's witty comebacks.

For my French readers, here's an example:

```text
LANDEYves: « Le piratage tue l'artiste »
Eolas: Ce n'est pas vrai. Je pirate depuis deux ans pour tuer
Florant Pagny et il est encore en vie.
```

## Watching the Eurovision

For those who do not know, Eurovision is a song contest that happens every year.

For French people, it's fun to watch because:

* we know we'll never win again, an
* it's so "kitsch" it's impossible to take it seriously.

I remember following the `#LTEV` hash tag, before it was "official".

Displaying all the tweets with the hash tag while watching this silly TV show
was doable because there was only a few people twitting about it.

Plus, every year, you could watch the show live on TV, follow the hash tag on
your computer, and re-unite with people who made you laugh the year before.

I don't watch Eurovision nor try to use the hash tag anymore.

The hash tag is now displayed continuously during the show, and there's just too
many people using it to read everything in real time.
Also,  it feels like that people only tweet in order to have their tweets displayed on TV,
and lots of tweets take the show much too seriously for them to be fun anymore.

I guess it's the end of an era.

## Saving content

Since the last 10 years of so, I keep interesting *fortunes* in a
private git repository.

Each file corresponds to a category, and inside the files, quotes are separated
by the percent sign and an index[^1], like this:

```text
# in fortunes/movies
%1
Elwood: It's 106 miles to Chicago, we got a full tank of gas, half a pack of
cigarettes, it's dark, and we're wearing sunglasses.
Jake: Hit it.
	The Blues Brothers
%2
- How much time before the collision?
- If its speed remains constant... in an hour and 57 minutes.
- I'll call you back in two hours.
    - The Fifth Element
...
```

```text
# in fortunes/series
%1
Snyder: Kids today need discipline. That's an unpopular word these days,
"discipline." I know Principal Flutie would have said, "Kids need
understanding. Kids are human beings." That's the kind of woolly-headed liberal
thinking that leads to being eaten.
  - Buffy the vampire slayer
%2
- I need out of here, now
- Anywhere in particular?
- Well, let's see. You've got a time machine, I've got a gun.
  What's the hell? Let's kill Hitler.
  - Doctor Who
...
```

So, naturally I started keeping interesting tweets in a `fortunes/twitter` file.

I still do this to this day. Here are a few taken from last year's Trump election:

```text
American friends: Trump isn't the answer.
(Unless the question is: "what would you obtain if a blobfish could fuck a
haystack?")
  @Boulet
```

```text
Ok, don't panic… If we hold the North and South Pole down simultaneously for
eight seconds, it'll automatically restore to factory settings.
  @_Enanem_
```

```text
America, you broke the build
  @ThePracticalDev
```

All those files are hosted on a private server, and I have a little command
line tool that allow me to randomly display a fortune taken from the whole
"database".

It's called *pyfortunes*, and you can find the source on
[github](https://github.com/dmerejkowsky/pyfortunes).

## Creating an account

Around the same time I started this blog, I decided to create a twitter account,
with the goal of trying to publish at least one tweet per day.

I failed at keeping my "one tweet per day" rules, but I still tweet about:

* Links I find and end up on the https://dmerej.info/links page
* Every new blog post
* Some nifty tips and tricks, mostly for the command line or the *vim* and *neovim* text
  editors.

At the time of writing, I'm followed by around 40 people, which is not much.

Most of them are friends, past or present colleagues, and a few acquaintances.

Also, `@climagic` follows me and that makes me very proud.


## Keeping control over my data

Shortly after posting my first tweets, I decided I needed to have a complete
backup of all the tweets I wrote.

Of course, twitter provides a way to get a backup of all your personal data in a
zip, but I did not want to depend on twitter being nice.

So I wrote a small script that I can run frequently in a systemd timer job that:

* Looks for the latest backed up tweet
* Fetches all the newest tweets and write them in a `.json` file
* Generates a completely static version of the timeline as pure HTML (with
  good old pagination instead of infinite scrolling)
* Writes all the text in a *sqlite* database so that I can run full text
  searches

Source code is [on github](https://github.com/dmerejkowsky/static_tl), and you
can see it live [on my website](https://dmerej.info/tweets/d_merej/index.html).

There's even [an RSS feed](https://dmerej.info/tweets/d_merej/feed.atom)
if you like old 90's tech ;)

## Twitter fatigue

Every night, I would go to `twitter.com`, and then scroll down again and again
until I find a tweet I've already read.

But as time passed, and the list of the people I followed grew, I found myself
spending more and more time reading my timeline.

The "signal v noise" ratio was very low.

For instance, I used to follow the [parodic Bill Murray account](https://twitter.com/BiIIMurray).

There was a few of his tweets that made me laugh, such as:

> Never go to bed angry. Stay awake and plot revenge

or

> The fact there's a highway to hell and only a stairway to heaven
> says a lot about anticipated traffic numbers.

but some of them were links to pages of a website I did not like at all.[^2]

In the end, I was following more that one hundred people, and it took me about
half an hour after work [^3] to go through all my timeline and find the one tweet I
already read the previous day.

It was a tedious process, because if I lost my current position in the timeline, I had
to go through everything back from the top.

A lot of the tweets I read during this process contained links, but I was so
concerned about loosing my position in the timeline that I opened them in a new
tab and continued scrolling before actually reading them.

So, after I was done with the scrolling, I still had a dozen of tabs opened
in my web browser, but I'd lost all context (no way to know what exact tweet
lead me to the page I was reading), and I was already exhausted by all the
information I had to process.

Jeff Atwood[^4] said it best:

> Twitter (n): a collaborative game where you try to guess what just happened
> based on a stream of truly awful jokes about the event.

## Fixing my timeline

It was then I decided to massively unfollow people.

No more Bill Murray, no more accounts that published interesting stuff 50% of
the time, no accounts that were only re-tweeting popular tweets ...

I went from following about one hundred accounts to less than twenty, and I decided
to never go above that number again.

Now every night I spend less that a minute reading all the things I missed while
I was working or sleeping, and the signal versus noise ratio is much better.

I'm also using a native client named [corebird](https://corebird.baedert.org/),
which allows me to go from this, as seen on twitter.com:

![twitter.com too much info](/pics/twitter-com-tmi.png)

to this:

![tweet-on-corebird](/pics/tweet-on-corebird.png)

Same data, but with a whole less of noise, don't you agree?


## Conclusion

Well, that's my story. If you are on twitter and follow a lot of people, I
highly recommend you at least take a good look at the list of the people you
follow, and ask yourself: "Do I really need to follow this account? Are _all_
his tweets interesting, or do they contain lots of noise?".

Using a dedicated application instead of keeping one tab of your browser opened
all the time on your timeline may help too. (You'll get a lot of spare RAM as a
bonus, by the way ...)

Well, that's all I had to say. Hopefully now you can understand a bit better why
I'm [trying to write a new twitter clone](
{{< ref "post/2017-01-06-how-to-build-decentralized-social-networks.md" >}})
with an hard-coded maximum of users.

There's more to this "decentralized social website" of course, so stay tuned for
more.

In the mean time, here's a nice article around the same subject:
[Quit Social Media. Your Career May Depend on It](
https://mobile.nytimes.com/2016/11/20/jobs/quit-social-media-your-career-may-depend-on-it.html)

See you soon!

[^1]: It's loosely based on the venerable [fortune Unix program](https://en.wikipedia.org/wiki/Fortune_(Unix)) format, but without the binary stuff.
[^2]: *twentywords.com*, if you must know
[^3]: I almost never read twitter at work, I just don't have time for it.
[^4]: You know, the guy behind the [coding horror](https://blog.codinghorror.com/) blog
