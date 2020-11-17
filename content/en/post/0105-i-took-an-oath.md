---
authors: [dmerej]
slug: i-took-an-oath
date: "2019-09-26T18:53:23.457560+00:00"
draft: true
title: "I took an Oath"
tags: [misc]
summary: I took an oath as a programmer and maybe
 you should consider doing the same
---

# Introduction

On November 15 2015, Uncle Bob published the [Programmer's Oath](https://blog.cleancoder.com/uncle-bob/2015/11/18/TheProgrammersOath.html) on
his blog, followed by an [explanotory article](https://blog.cleancoder.com/uncle-bob/2015/11/27/OathDiscussion.html)>

I strongly advise you go read them. Even if I don't agree with everything he says, I find it a worthy read.

He's also produced an [hour long video](https://cleancoders.com/video-details/clean-code-episode-45) on the topic that I also recommend watching.


# Why I took the Oath


I think a good first step towards more ethics in the programmer's profession is for
_individual_ programmers to make the decision to take this oath. For me, any programer is,
free to keep practicing his profession without taking it, it has to be a _personal choice_.

In the same vein, the oath does not have to the same for everyone!

That's why, as a symbolic gesture, I've published a copy of the Oath [on my personal website](https://dmerej.info/oath.md) signed with my GPG key.

It contains two additions compared to the original 9 rules written by Uncle Bob, that I would like to discuss here.

Two reminders before we dive in:

* You may find the rules stupid or weird. That's OK. Remember, I
  believe that the decision to take the oath and the contents of the oath should
  be personal. You don't have to agree with me on this.
* You may find the rules impossible to follow in practice. Yes, being totally ethical
  at work is an _ideal_. The text starts with "to the best of my ability and judgement".
  You should see those rules as goals to work towards, not necessarily achieve at all costs.


# Ethics in communication

> In all my communications (especially written and public ones), I will
> not allow myself to be offended by what people say to me, but I will
> do everything I can to not offend the people I speak to.

You'll notice that the rule is fundamentally _asymetric_: it puts a lot of duties on me, and absolutely nothing no others. That's by design and one of the reasons I love it.

Anyway, the first part of this one is basically the [Crocker's Rule](), that I have been following,
since this blog was born. Crocker's Rule works best when both participants of the conversation
agree to follow it, but it also allows a "downgraded mode" of communication if only one of the participant follow the rules.

The second part is there to acknowledge that lots of people can get offended by lots of things, especially in the case of written exchanges with strangers. There are a lot of basic rules you can follow - think of the "Code of Conduct" you may find on an open-source project, for instance, but it's also a _process_.

For instance, I learned to say "Hi, there", or "Hi, everyone!" instead of "Hi, guys", after reading some feminists testimonies online feminists

An other example. I live in Paris, France and one day I wrote about an event taking place in Paris to a broad French-speaking audience, without explicitely specifying the name of the city. You might not know this but a _lot_ of Parisians do this, and almost _no-one_ leaving outside Paris does the same thing. When it was pointed out to me, I apologized and thanked the person for letting me know.

# Ethics in data processing

> I will not store more data than it is absolutely required, and I
> will not allow any data loss nor unauthorized acces or modification.

You could see this one as just a repition of _the law_ (especially with the latest
changes in cookie policies or GDPR), but for me it goes beyond that. Let's break it down.

"Not storing more data than is absolutely required": there are two reasons for this:

* One, our profession is consuming more and more resources and there's no need to waste them.
* Two, the eaisest way to prevent data leaks, or members of staff accessing to private data is simply to _make sure it isn't there_. For instance, you don't *have* to log everything every single thing every user of your application does. You can use sampling techniques to only record _parts_ of the activity, make sure to anonymize data _before_ storing it, and so on.

"I will not allow any data loss". This may sounds strange. After all, most of us when thinking about data loss would just say: "I'll just do incremental backups every day", and if something really goes wrong I'll restore them and only lose 1 day worth of data. How bad can it be?

Well, the problem with this approach is that you can never know in advance how _valuable_ the data is! Most users of your applications will assume it contains no bugs and that no data would be lost, ever (unless you market it as a feature, of course). TOOD: find an example


# Conclusion

More than ever, your feedback is welcome here. What do you think of having a common oath for all developers? What do you think about taking one? What is your opinion of my added two rules?

Please leave a comment below and let's discuss ethics for a change!
