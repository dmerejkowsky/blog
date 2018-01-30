---
slug: additions-to-how-to-prepare-a-talk-by-gary-bernhardt
date: 2018-01-26T13:08:59.210468+00:00
draft: false
title: |
  Additions to: "How To Prepare A Talk", by Gary Bernhardt
tags: [talk]
---

Recently, Gary Bernhardt, from [destroyallsoftware](https://www.destroyallsoftware.com/), posted an article entitled [How To Prepare A Talk](https://www.deconstructconf.com/blog/how-to-prepare-a-talk).

I highly recommend you read it, it contains lots of good advice.

I myself have given quite a few talks, but in a slightly different context: I was sent by my company.

This changes a couple of minor things, so I though I could add a few points to the original article.

<!--more-->

# Buy a laser pointer

![laser pointer](/pics/laser-pointer.png)

This little device will make you look cooler and more professional.

I made my company pay for one that looks just like the above picture. It comes with a USB connector and emulates the left and right keys of a keyboard. It works on any operating system and with any presentation software.

By using this, you won't have to point to things at the screen with your hand, and you won't have to go back to your computer every time you need to switch to the next slide. This will help you achieve a more steady flow.


# Rehearsal

After you've done enough repetitions to have a talk _you_ like, and before the actual event, I suggest you do at least two rehearsals with some team mates.

## First rehearsal

### Preparation

* Book a room for about twice the expected time of your talk.
* Make sure each slide is numbered.
* Ask each participant to come with pen and paper.

### Talk itself

Give the talk as you would in front of a live audience. Assume your team mates know almost nothing about what you are talking about and who you are.

Ask one of them to time the rehearsal so that know if you still need to cut something.

If your talk contains jokes, questions, or any other interaction with the audience, it's a good way to make sure they work.


### Feedback

Once the talk is done, it's time to get feedback.

Based on my experience, asking each participant to give its comments one at a time does not work very well.

* Most of the participants in the meeting will get bored because they are just waiting for their turn to speak.
* There's a high risk of repetition.
* If they discover they disagree about something, they won't be able to discuss it right away.

Instead, go back to the beginning of your slides, show them one by one, and ask about feedback from everyone at the same time. That way:

* If they agree about something, they'll say it together and you're more likely to remember it.
* If they disagree, you'll have an opportunity to discuss things right on the spot.

## Second rehearsal


The second rehearsal is a way for you to reflect on the feedback, do more work by your own and finally do one last repetition.

For the second run, invite a mix of people who:

* Were there the first time, so they can see the progress from the last run.
* and were not there the first time, so they can bring a fresh perspective.

Resist the urge to change too much things after this point. It's probably too late and further changes will only confuse you.


# The big day


## Be there early

Of course, you don't want to be late, so you should plan your travel accordingly to make sure you get there on time with a sufficient error margin.

But it's even better if you are on location *before* any talk.

If you can, plug your laptop to the screen and make sure everything is OK, but really the best thing to do is to take the opportunity to make friends with some of the tech people and organizers.

They should not be too busy at this point, and it's always good to have them on your side :)


Speaking of friends:

## Don't go alone

True, your company may save a few bucks by not paying for an other transport, but you'll be happy to have someone who can provide moral support on the big day. (Especially if you are in a foreign country).

Also:

* You'll have an accomplice in the audience who will be able to laugh at your jokes, ask the correct questions, or otherwise influence the audience in more or less subtle ways to help you.

* You'll get honest feedback about your performance. It's a good idea to let him record you, so that you have a way to see how you were doing. Note that watching yourself talk looks very weird, but it's a great way to discover what can be improved.

* Your accomplice will also be able to help you during Q&A.

# Q&A

Just one advice here: **repeat the question before answering**.

* Most of the time, questions asked during a recorded talk are hard to hear (or not audible at all), so repeating the question will help future watchers understanding what's going on.

* If you don't like the question, you can rephrase it slightly to be any question you want and answer _that_ instead. By being the speaker in a talk, you have more power than any one in the audience, so use it.

# Do it live!

This is a live performance, so do _something_ live.

Here are some ideas:

* At the beginning of the talk, tell people they can interrupt you any time if they have questions. This work well if your main goal is to *teach* something to your audience.
* If you are talking about a product, do a live demo about it.
* Do some live coding (people seem to love those)

Once upon a time, I did a live session about TDD, in C++, on Windows, by running `cl.exe` from `git-bash`, even though my only experience so far was doing TDD in Python on Linux.

It went really well, and the key, as always, was to **repeat the demo** enough times until I knew it by heart and could do it with my eyes closed.

Note that it really helps if you memorize any setup or cleanup you may have to do and do it at the _end_ of each practice run. That way you won't have to care about setup on the big day.

Last but not least, have a backup plan in case there's no Internet connection. It happens more often than you think, especially if WIFI is involved[^1]. So, prepare something like a pre-recorded video, screen shots, or something else to talk about.

By the way, if your live demo involves typing things in a terminal, you may want to try using the aptly named [doitlive](https://doitlive.readthedocs.io/en/latest/) tool, and if you want to publish a recording of your command line session, [asciinema](https://asciinema.org/) works great.

# Conclusion

I hope you'll find some of this advice useful. I too learned quite a lot from Gary's article, so naturally I wanted to share some of my experience with you.

Before I go, one last "meta" advice. If you want to get better at giving talks, just do one as soon as you have an opportunity, especially at work. You can start by talking about technical stuff to the rest of your team and in a place you know well, and move on to bigger events and broader audiences later.

Cheers!

[^1]: Except at [FOSDEM](https://fosdem.org), because FOSDEM  tech guys rock.
