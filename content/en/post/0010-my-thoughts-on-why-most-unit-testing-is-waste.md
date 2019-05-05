---
authors: [dmerej]
slug: "my-thoughts-on-why-most-unit-testing-is-waste"
date: "2016-06-04T18:08:42+02:00"
draft: false
title: "My Thoughts on: 'Why Most Unit Testing is Waste'"
tags: ["testing"]
---

Last week a friend of mine sent me on IRC an article called *Why Most Unit
Testing is Waste*.

This was written by James O'Coplien, and you can find the original .pdf
[here](http://rbcs-us.com/documents/Why-Most-Unit-Testing-is-Waste.pdf)

We had a quick chat afterwards, and I'd like to sum up what was said here.

<!--more-->

# Important notice:

Following the publication of this article, I got an e-mail
from James O'Coplien himself. He said, among other things:

> I think you maybe want to significantly update or remove the article to avoid
> embarrassment to yourself

Well, turned out I was victim of a well known syndrome: The Expert Beginner,
to quote a good article from Eric Dietrich:
[How Developers Stop Learning: Rise of the Expert Beginner](
http://www.daedtech.com/how-developers-stop-learning-rise-of-the-expert-beginner/)

So I'd like to thank James O'Coplien for showing me that I had still many
things to learn on the subject. I may also have misunderstood things he wrote.

Anyway, feel free to continue reading, but please take everything I say below
with a grain of salt ...

Also, don't hesitate to give me feedback on this, see
[the dedicated page]({{< ref "/pages/contact.md" >}}) on how to reach me.



# Introduction

The following sections directly came from the original article, so you should read
them first to understand what I'm talking about :)

You should also know that I'm using my own experience of several years
of Test Driven Development in one of my projects to make my remarks.

## 1.1 Into Modern times

Nothing to say here, it's a good summary of what happened from the old days of
FORTRAN to the modern age of Object Oriented programming with *classes*.

## 1.2 The Curse is Worse than the Disease

In this chapter there's an interesting quote:

> Today however, my team told me the tests are more complex than the
> actual code.

That's really weird. In my experience, when I have complex production code,
it usually means there are lots of simple tests to make sure all the
corner cases are handled. But the code of the tests themselves are really simple:

* Prepare the environment
* Exercise the production code
* Make some assertions (usually only one)

> To do complete testing, the number of lines of code in unit tests would have
> to be orders of magnitude larger than those in the unit under test

We'll go back to that. But just so you know, in my project I have

* 80% line coverage
* 11260 lines of tests
* 27775 lines in total.

The test code represents about 45% of the whole code base.

> "Every line of code has been reached," which, from the perspective of theory
> of computation, is pure nonsense in terms of knowing whether the code does
> what it should.

I agree with that. I've even seen a project which had 100% code coverage, and won't
accept any pull requests that would decrease the coverage in question.

Yet it had some serious bugs, that would have been caught if only the examples
in the documentation were tested ...

You can see the bug fix I wrote [here](https://github.com/crsmithdev/arrow/pull/321)
if you are interested.

## 1.3 Tests for their Own Sake and Designed Tests

> I had a client in northern Europe where the developers were
> required to have 40% code coverage for Level 1 Software
> Maturity, 60% for Level 2 and 80% for Level 3, while some
> where aspiring to 100% code coverage

Wow. Just wow. Is this silly. Even without using TDD, there's no
reason not to have good coverage **from the start**.

An exception is when you have "spikes": that is, when you code something
as quick as possible, and cutting a lot of corners just to see if you
are on the right track or not.

But even then, by the end of the spike you're supposed to throw away
all this "proof of concept" code and rewrite it with good coverage.

> If you find your testers splitting up functions to support the testing
> process, you're destroying your system architecture and code comprehension
> along with it

I could not agree more: both the production code and the test code should
be clean.

What do I mean by that?

* If tests are difficult and painful to write, it may mean you have a
  problem in your production code (since well designed code should be easy to
  test), or maybe you have a problem in the tests themselves, and you have
  to *design* a better test framework.

* But if your tests prevent you from refactoring because they always fail
  for no good reason, you should throw them away and think more about
  how to write better tests. Usually the reason is that they are too close
  to the implementation: as they say, *test the interfaces, not the implementation*


> I define 100% coverage as having examined all possible combinations of all
> possible paths through all methods of a class, having reproduced every possible
> configuration of data bits accessible to those methods, at every
> machine language instruction along the paths of execution ...
> If you plug in some typical numbers you’ll quickly conclude that you’re lucky
> if you get better coverage than 1 in 10 <sup>12</sup>

Yes. That's why aiming 100% test line coverage is silly. Let's take a
simple example.

```python

def foo():
    if a:
        do_this()
    if b:
        do_that()
```

You can achieve 100% line coverage by writing two tests:

* One with `a=True` and `b=False`
* One with `a=False` and `b=True`

But of course, the number of possible combinations is four,
and nothing tells you that you won't get a crash if both `a` and
`b` are true at the same time.

The total number of possible states for the program thus grows
much, much quicker than the number of lines, (it's probably
a exponential law)

So what can you do? Well, when you're doing TDD you'll usually write
a "happy path", that is, describing what should happen in the nominal
case, and then write a few tests for the corner cases you are currently
thinking of.

I hope by now you better understand what the author was saying at
the beginning:

> Unit tests are unlikely to test more than one trillionth of the functionality
> of any given method in a reasonable testing cycle. Get over it.

Yet, measuring line coverage does have some value:

* First, it can be used as an incentive to write more tests, although in my opinion,
  trying to reach more than 80% is too much.

* Second, it can help you spot dead code, and getting rid of dead code is a
  Good Thing™


Then the author talks about automation, saying something like:

> You'll probably get better return on your investment by automating
> integration tests, bug regression tests, and system tests than by automating
> unit tests.

I also agree on that. The tests you write during TDD are often trivial to
automate (otherwise, doing TDD is simply not doable), but they cannot
cover everything (see above)

So of course you need higher-level tests, and automate them! Don't waste time
and money hiring unqualified people to run your "high level" tests by hand when
you can automate the process. You'll get an even more return on investment if
*developers* themselves are writing the high level tests, because when tests
fail, they'll know if it's because the tests is not written correctly, or if
it's actually a bug.

I'm not saying you should not have a dedicated QA team (after all, you can
always have a few tests that are very hard to automate), but I'm saying you
should not let your developers only write low-level tests, which I believe
is also the message the author is trying to get across.

> Do formal boundary-condition checking, more white-box testing, and so forth.
> That requires that the unit under test be designed for testability.

Yes and yes.

Here's one [talk](https://www.destroyallsoftware.com/talks/boundaries) about the
boundary stuff.

Also, to cite Uncle Bob (Robert C. Martin), from [Given Up on TDD](
http://blog.cleancoder.com/uncle-bob/2016/03/19/GivingUpOnTDD.html)

> **Something that is hard to test is badly designed.**
>
> Suppose you ask me to write an app to control your grandmother's
> pacemaker. I agree, and a week later I hand you a thumb-drive and tell you to
> load it into her controller. Before you do you ask me: "Did you test it?" And my
> response is: "No, I chose a design that was hard to test."
> ...
>
> Let me drive that home even more.
>
> Any design that is hard to test is crap. Pure crap. Why? Because if it's hard to
> test, you aren't going to test it well enough. And if you don't test it well
> enough, it's not going to work when you need it to work. And if it doesn't work
>  when you need it to work the design is crap.

## 1.4 The Belief that Tests are Smarter than Code Telegraphs Latent Fear or a Bad Process

I've not much to say about this section, but here are two quotes worth
remembering:

> It's much easier to avoid putting bugs in than to take them out.

And:

> If you have comprehensive unit tests but still have a high failure rate in
> system tests or low quality in the field, don't automatically blame the tests
> (either unit tests or system tests). Carefully investigate your requirements
> and design regimen and its tie to integration tests and system
> tests.

## 1.5 Low-Risk Tests Have Low (even potentially negative) Payoff

This section is really interesting.

If "1" is the passing of a test and "0" is the failing of the tests, the
author says, what's the values of a test that look like:

```
1111111111111111111111111111111
```

versus a test that looks like:

```
1011011000110101101000110101101
```

Using information theory, he deduces that the second test contains much more
information that the first one.

So, he argues, you should get rid of the first one, and only keep the second.

> You see, developers love to keep around tests that pass because it's
> good for their ego and their comfort level.

I can relate to that :) But one good way to fix that is to not hesitate to
remove those tests when doing some large refactoring, where making them
still pass would be too costly.

> In most businesses, the only tests that have business value are
> those that are derived from business requirements

Maybe, but I think the author is overlooking some aspects of doing
TDD here.

Let's recap the 3 steps of the TDD cycle:

* Write a test that fails (Red)
* Write the minimal amount of production code to make the test pass (Green)
* Refactor the production code to make it cleaner, and keep the tests
  passing (Refactor)

By writing a *failing* test first, you know you're not writing a "tautological"
test.

*Update: what I just said is simply untrue. If you write*
```python
def test_foo():
    assert foo() == 42
```

*and then*

```python
def foo():
    return 42
```

*it _is_ a tautological test that tells you absolutely nothing.*

*I went and looked back at some of the unit tests I wrote and did not find any,
but that does not mean it can't happen.*


Also, by writing tests first, you have to think of the API of your production
code right before writing any implementation, so TDD actually help you
better design your production code. (It's a **huge** win)

Lastly, by constantly refactoring your production code, you have clearer
and more maintainable code, which is also good for business.

## 1.6 Complex Things are Complicated

I've got nothing to say about this section, let's move on ...

## 1.7 Less is More, or: You are Not Schizophrenic

A few words about the "schizophrenic" thing.

One of the things that's really hard when writing code is that you see only a
few lines of code at one given time, and yet you have to think about how it
will be used by other parts of the code.

TDD is interesting since it forces you to think about your code from a
"testing" point of view.

I also found out that by simply writing *documentation*, I was seeing the code
from yet another point of view, and this lead to a better design.

So yeah, you do have to be a little "schizophrenic" if you want to have good
design :)


> "Oh, you have to invoke Maven with this flag that turns off those tests — they
> are tests that no longer work because of changes in the code, and you need to
> turn them of"

Back to the fear of removing tests. Again, if your refactoring make the tests
fail, remove them and write new ones with your new design in mind.

> The most common practice — which I saw at a startup where I used to work back
> in 2005 — is to just overwrite the old test golds (the expected output or
> computational results on completion of a given test) with the new results.

Yeah ... Please don't do that. When you have a bug, write a *failing* test
first, and then watch it pass when you do your bug fix.

*Update: two things here:*

*One, using TDD to fix bugs may not be a good idea (see [my post "When TDD
Fails"]({{< ref "/post/0014-when-tdd-fails.md" >}}) for more)*

*Two, the author is actually not talking about bug fixing: he's saying that
when you change code, sometimes tests fail and you simply overwrite the tests
golds without thinking too much about it, assuming your production code is
correct. I've also added a section in the same post about this.*


> Psychologically, the green bar is the reward.

True story: after years of TDD, the *red* bar is the reward for me.

If I'm trying to fix a bug, it means I've finally found a way to reproduce
it, which is clear progress towards a fix.

If I'm implementing a new feature, I know I have a good idea on how to implement
it and how it's going to be designed, which means I can leave work, and come
back the next day with just a straightforward implementation to write :)

The green bar is just a quick check before or right after I publish my changes.

## 1.8 You Pay for Tests in Maintenance — and Quality!

> One technique commonly confused with unit testing, and which uses unit tests
> as a technique, is Test-Driven Development.

Let's keep this quote in mind for now, and go back to it later ...

> You need to think of tests as system modules as well.

I don't really agree on that. What I've experienced is that the skills required
to write good production code are **different** than those required to write
good tests.

So to be good at writing tests, you should practice the same way you've learned
to program in the first place: by making mistakes and learn from them.

> Turn unit tests into assertions

Hum. I'm really not sure about that. I've been successfully maintaining a Python
project for several years without having a single assertion in the production
code. But maybe that depends on the programming language, I don't know.

But, following the "professional approach" the author describes, I've never
tried to hide errors: any uncaught exception would trigger a very detailed
backtrace that could be used for bug reporting.

> "the next great leap in testing is to design unit tests, integration tests,
> and system tests such that inadvertent gaps and overlap are removed."

Yup. And TDD can actually help you do that. More on this later.

## 1.9 "It's the process, stupid" or: Green Bar Fever

> Debugging is not testing. It is ad-hoc and done on a bug-by-bug basis. Unit
> tests can be a useful debugging tool.

Yup. As I said, for me the goal is to have a *failing* test when I'm trying
to fix a bug.

Usually it starts as a system test, and then I write more and more and more low
level tests until I find the root cause. I usually get rid of most of the test
code I wrote afterwards, leaving just enough tests to have regression testing.

## 1.10 Wrapup

> However, many supposedly agile nerds put processes and JUnit ahead of
> individuals and interactions.

Please don't do that. TDD is just a tool to help you write better code, but
you should always put the human first: your code is going to be read by other
humans, and if you can't communicate with them, you're doomed to fail, no matter
how good your process is.

> Be humble about what tests can achieve. Tests don't improve quality:
> developers do.

Yes, but I still believe having developers do TDD make them better :)

# Conclusion

The message of the author is that most unit testing is waste, that TDD
is mostly concerned with unit test, and that you should focus more on system and
regression testing.

I'd like to respond to that by explaining how I write tests during TDD, for
instance when implementing a new feature.

I usually start by writing some documentation or specification: this way, we
can quickly see if it's a good idea or not, and make progress on the design,
without writing a single line of code.

Then I write a high level, failing, system test. (I usually have a framework for that).

Then I start working on the implementation, and write some unit tests only when
I have a very good idea on what the *interface* of the various modules I'm
writing will look like.

I often make mistakes, because some problems only become visible when you are
busy writing the implementation.

When that's the case, I often take a break, and then discuss with other people
on how to fix the issues I've just seen. Maybe the feature is too complex to
implement, maybe the specs need to change, and so on...

So, yeah, unit tests and TDD are just a small part of the whole picture, but
remain valuable tools anyway.

Well, that's all I had to say. Thanks for reading!
