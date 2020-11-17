---
authors: [dmerej]
slug: a-simple-problem
date: "2016-11-20T14:54:11.710423+00:00"
draft: false
title: A Simple Problem
tags: ["misc"]
---

Let's say that at your work, you have daily meetings every day at 10.

To avoid monotony, you've decided to signal the beginning of the meeting by
playing a different song every time.

Let's assume the following:

* Your music collection is organized neatly, and all the
  file names look like `<author> -<title>.mp3`
* The files can be found and downloaded easily from a web browser.

You'd like to:

1. Make sure to never play the same song twice
2. Be able to answer the question: "What was the song you played X days ago ?"
3. Have a chronologically sorted list of songs, so that you can tell yourself:
   "Hum. It's been two weeks I did not play anything from Pink Floyd, let's
   use _Another Brick In The Wall_ today"


Based on your experience, how many lines of code do you need to write to solve
this problem?

<!--more-->

I'm going to give you a moment to think about this ...

Enjoy the video in the mean time:

{{< youtube id="VwO21W9AD3w" autoplay="false" >}}

So how much was it? One thousand lines of code, one hundred, ten?

I know you are going to say it depends on the language you are using, but in
reality it does not.

The number of line of code you need to write does not depend on the language
you are using because the answer is zero.

{{< spoiler >}}

You just need a special folder, let's say "Stand Ups" and a file explorer.

Every day, you download your song in the correct folder, and then you use
the "sort by date" feature to have your songs sorted by date:

![Stand Up folder](/pics/standup-folder.png)


Yup, sometimes "do nothing" is the best strategy :)

I'll leave you with a quote and a link:

> The cheapest, fastest and most reliable components of a computer system are
> those that aren’t there.
>
>   -- Gordon Bell

* [You Are Not Paid to Write Code](
  http://bravenewgeek.com/you-are-not-paid-to-write-code/)

Bye!

{{< /spoiler >}}
