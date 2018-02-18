---
slug: helping-bbc-subtitlers
date: 2018-02-18T13:52:40.203284+00:00
draft: false
title: Helping BBC subtitlers
tags: [ideas]
---

# Introduction

The other day I stumbled upon an article called [Why subtitlers have one of the hardest jobs in TV](http://www.radiotimes.com/news/tv/2018-01-24/how-do-tv-subtitles-work/). Go read it now, I'll wait.

That got me thinking. What if there was a better way to transcribe what is said on TV into proper text, without having humans trying to repeat what they heard in a robotic voice, and then not-so-good "speech to text" programs converting robotic human voices to words?

<!--more-->

# An idea using old tech

Turns out that writing text as fast as it is spoken is a very old problem. It's called *stenography* (or shorthand), and according to [Wikipedia](https://en.wikipedia.org/wiki/Shorthand), it's been around since classical antiquity.

Heres's what *stenography* looks like using the French "Prévost-Delaunay" technique:
![stenograpy example](/pics/steno.png)

In the same vein, converting human hand-writing to text is also a well-known problem. Just take a look at [OCR history](https://en.wikipedia.org/wiki/Timeline_of_optical_character_recognition).

Speech recognition is quite new in comparison, and even if it has improved in the last decades, it's still not entirely reliable, as the radiotimes article shows.

So here's the idea:

First, train people in stenography. In French, there used to be a job called "sténo-dactylo", a secretary who used shorthand techniques to transcribe speech into an optimized hand-written notation, and then re-entered the text on a typing machine.

To be trained in stenography can be useful in a bunch of situations. For instance, sometimes video or audio recording is prohibited by the law, and it's up to a court clerk to transcribe everything that is said during a trial: see [this scene from "intolerable Cruelty"](https://www.youtube.com/watch?v=BxQMT4R51Dk) for an example.

Note how the problem of punctuation goes away, because you can just *write* `?` instead of saying "question mark".

Also, the issue of coloring the subtitles with different colors depending on who's speaking could be solved by inventing a notation, like prefixing the spoken words by the name of the speaker.

Then, tweak an OCR Software so that it can work with the kind of input shown above. This may be a bit tricky because most of the time, the stenography techniques use a "phonetic" system, meaning that "eye" and "I" would both be written the same way. But I think we could train the software to automatically deduce the correct spelling.

There's also the issue of proper nouns, but maybe we could fall back to regular writing for those.

Looks to me this would cost less in R&D, and could also lead to a better quality of life for the subtitlers. No more sore face at the end of the day, and no more voice tics.


# An even simpler idea

While I was doing research for this article, I found that there's also a job called STTR. The "Speech To Text Reporters" use a dedicated machine, as seen [on this demonstration video](https://www.youtube.com/watch?v=egLLsM9wN50).

This seems to be already working just fine! Note how the names of the person speaking are handled, and how it's a fully regulated profession. STTRs type **at minimum** 180 words per minute and with 97% accuracy, and are tested in live situations.

There's a tiny issue because speech to text reporters have both their hands busy all the time, which means it would be hard for them to modify the position of the subtitles in real-time. But I believe the task of finding a 'text-free' zone in the image and automatically move the subtitles could quite easily be done automatically by a small piece of software.

So the question become: what was the reason for the BBC not to hire STTRs for the purpose of subtitling all their programs?

I don't have the answer, but if you ever need real-time speech to text conversion, please consider using a different technique than "respeaking".
