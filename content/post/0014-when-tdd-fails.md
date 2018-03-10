---
slug: "when-tdd-fails"
date: "2016-07-02T16:14:52+02:00"
description: ""
draft: false
title: "When TDD Fails"
tags: ["testing"]
---

Some random thoughts about TDD ...

If you already know about TDD, feel free to skip the introduction and go
directly to the <a href="{{< relref "0014-when-tdd-fails.md#when-tdd-fails-main" >}}">main section</a>

<!--more-->

# Introduction: What is TDD?

TDD is short for "Test Driven Development". According to
[Wikipedia](https://en.wikipedia.org/wiki/Test-driven_development), it's a
"software development process that relies on the repetition of a very short
development cycles".


## The Red, Green, Refactor loop

The process is fairly simple:

* First, you write a failing test.

* Then, you modify or add new code so that the test pass. The code under test
  is often called the  "production code".

* Then, you refactor the code if you need too, making sure that all tests pass.
  Note that at this point, you are allowed to refactor both the test and the
  production code.

And then you restart the loop.

Note that:

* You are not allowed to add new production code without a failing test first.

* You are not  allowed to add more production code than is required to make the
  test pass.

## Rationale

### Write a Failing Test First

Having a test that fails at first is a good thing, because you can know the
test is actually testing something, and is not doing a sophisticated version of

```python
def test_foo():
    assert 2 == 1 + 1
```

In case of adding a new features, writing the test first forces you to think
about the testability of the new code you are going to write, which may seem a
waste of time.

But code that is easy to test is easy to change, and the fact that
the code is testable usually means there is a good decoupling of concerns.

Writing the tests first also makes you think about the specifications of your
new features. If you do not have a clear set of specifications in mind, your
are not going to write good software.

Note that if the feature is complex, it's perfectly reasonable to write
specifications or documentation even before writing any production code or
test, that's a good way to get feedback. It may seem strange to start by
writing the documentation, but I've found this technique very effective: if
your design has to change, you'll be glad you'll only have to update the
documentation, and not re-write tests or production code :)

Last, but not least, writing the tests first makes you think about the
interface of the new code you are going to write, which is also a good thing:
clear and clean API also make for more maintainable code.

### Write the Minimal Amount of Production Code

By not writing more code than is required for the tests to pass, you can avoid
feature creep and over-engineered design. When writing the code to make test pass,
your sole focus is to implement the feature. You don't care about code quality here,
which is great because you get to concentrate on just that in the next step of the
loop :)


### Refactor Code When Done

First, a quick definition of "refactoring" : it's the process of *changing the
implementation without changing behavior*.

So, why do we do it? We do it so that *future* changes in the code will get
easier.

When adding a new feature or fixing a bug, there's always the temptation to
lower the quality of the code: "Well, I know this is no the cleanest way to do
it, but we'll have time to refactor later ..."

If you do not want to suffer from "technical debt", and keep being "agile",
i.e, be able to quickly adapt to change, it's crucial to be able to make
refactorings frequently.

Doing so right after the tests pass gives you confidence you are actually not
changing the behavior.

Note that you should be refactoring both your code *and* the tests: making sure
it's easy to write new tests is as important as making sure it's easy to add
new features to the production code. (I believe this is true even when you're
not doing TDD, and simply adding tests after production code is written).

It also means you may have to write a test framework, and of course have tests
for the test framework :P


# When TDD Fails {#when-tdd-fails-main}

Here's a list of a few things that happened to me when using TDD that I did not
expect, in no particular order.


## Using TDD to Fix Bugs

I'm going to use [this bug in Neovim](
https://github.com/neovim/neovim/issues/4979) as an example.

`Neovim` added an event called `TabNewEntered` that is triggered every time you
open a new tab. There are several ways to create new tabs in `Neovim`: the obvious
one is with `:tabnew`, but you can also use `<CTRL-W> T`.

So I started to write a failing test to reproduce the bug:

```lua
describe('with CTRL-W T', function()
    it('works when opening a new tab with CTRL-W T', function()
        clear()
        -- Tell Neovim to display a message when TabNewEntered is triggered
        nvim('command', 'au! TabNewEntered * echom "entered"')
        -- Open a new window with a split
        nvim('command', 'edit test.txt')
        nvim('command', 'split')
        -- Send the <CTRL-W> T key combination and check Neovim's output:
        eq('\nentered', nvim('command_output', 'execute "normal \\<CTRL-W>T"'))
    end)
end)
```

I then run the test and was please to see it fail:

<pre>
expecting: '\nentered' but got ''
</pre>

Confident I was on the right track, I opened an issue on `Neovim` bug tracker stating
I found a bug, wrote a test to reproduce it and asking for clues on how to fix it.

I received an answer with the patch, applied it, but the test was still failing.

Did you guess what was the problem?

Well, turned out there was a bug in the test I just wrote! Instead of
`:execute "normal \\<CTRL-WT>"`, I should have used `:execute "normal
\\<C-WT>"` :/

Several lessons here:

* While writing a short piece of code to try and fix a bug, always remember there may be
  a bug in the code you just wrote, too!

* I talked about tests frameworks before. While the one used by `Neovim` is quite good,
  maybe it needs a easier way to send keystrokes so that this does not happen again [^1]

## Exploring

Sometimes you just have no clue whether the solution you have in mind will work.

In this case, I think it's OK to write a bunch of code without any tests, just to
get more information about the problem you are trying to solve.

This is sometimes called "spiking".

But when the spike is over, you should consider re-writing the implementation
using TDD, which will make sure you both have a working solution *and* a good
design[^2].

## Performance Issues

When you are using `TDD` you need a very short "feedback loop". This means you should not
wait a long time while running the tests.

If they take too long, you are not going to run all of them, or you're not going to write them
first because it will constantly break your workflow.

So the result is you start to optimizing the *tests* performance, making sure they run fast.

This can lead to really big issues in the performance of your production code, that you may
never realize until you do some very high level integration tests, and even then, if you
do not generate big enough inputs, you won't see the issue until very late in the development
process.

Some ideas:

* Take some time during the "refactor" phase to think about performance.
* Use code review at the end of each loop so that bad algorithm complexity can
  be spotted
* Use "continuous delivery", and/or frequent releases so that those issues become
  apparent when people start using your software

The good news is that since you have an existing test suite that works well, you'll be
able to:

* Write code that exercise the parts that you think are slow and use it to
  measure things. (You *do* measure things before optimizing the code, right?)
* Once the bottleneck has been spotted, refactor your code with confidence.


## Design Issues

Initially, `TDD` was called `Test Driven Design`. Indeed, `TDD` is more of a
design technique than a test technique: in effect, you are designing your
production code from the tests.

This can leads to some problems, particularly if you only write "unit" tests.
It's easy to miss the "big picture" when you are always running short tests
that only exercise one class or one function.

In my opinion, the way to fix that is again to take some time during the
"refactoring" phase to think about design and architecture, and realize that
they are other ways to design your code than just the tests. I've already
talked about how documentation or specifications can help here.

## Overlooking Test Failures

Sometimes when you do TDD, you'll get test failures while being sure the
production code you just wrote is correct.

It may happen during "Refactor" phase, especially if you're
refactoring both the test and the production code in the same time, but also
when trying to go from the "Red" to the "Green" phase.

When that happens, you may be tempted to simply overwrite the test "gold"
with the actual outcome.

That is, after:

```text
in test_foo():
  assert foo() == 42
got 41, expecting 42
```

You'll just get the test to pass with:

```diff
def test_foo():
- assert foo() == 42
+ assert foo() == 41
```

Usually, this is a bad idea. What I've discovered is that you get *different*
kind of failures depending on whether you actually changed the behavior of the
production code, or just need to adapt the test code to your latest changes.

Whenever I change production code, I try to think about which tests are going
to fail *before* running them, and then I'm very careful if I see one failure I
did not expect.

Let's take an example to make things clearer. Let's say the Product Owner decides
we no longer want to make coffee without sugar.

The patch looks like this:

```diff
Subject: Product Owner said we always want sugar
--- coffee.py
+++ coffee.py
class CoffeeMaker():
-     def make_coffee(temperature, with_sugar=True):
+     def make_coffee(temperature):

```

I'm expecting some of the tests to fail with

```text
TypeError: make_sugar() got an unexpected keyword argument 'with_sugar'
```

But if I get an assertion failure, such as

```text
in test_shop():
  assert diabetic_client_happy == True
expected True, got False
```

that's a completely different story!


# Links

* [Wasting Time TDDing The Wrong Things](
  http://www.rubypigeon.com/posts/wasting-time-tdd-the-wrong-things/)
  Where you learn how to avoid "bottom-up" design, and use "top-down" design
  instead. I realized TDD worked really well for me when I was doing exactly
  that :)

* An other explanation about how TDD works and why by someone much smarter and
  experienced than me, Robert C. Martin, aka "Uncle Bob":
  [The True Rules of TDD](http://butunclebob.com/ArticleS.UncleBob.TheThreeRulesOfTdd)

* There also was an article written by Ian Sommerville called
  [Giving Up on TDD](
  http://iansommerville.com/systems-software-and-technology/giving-up-on-test-first-development/),
  to which Uncle Bob responded [here](
  http://blog.cleancoder.com/uncle-bob/2016/03/19/GivingUpOnTDD.html) , about
  problems TDD novices experience.

* A fascinating debate between Uncle Bob and Jim Coplien about TDD on
  [youtube](https://www.youtube.com/watch?v=KtHQGs3zFAM)

* A scientific study on the effects of using "test first" or "test last" during
  development:
  [Does Test-Driven Development Improve Software Design Quality?](
  http://digitalcommons.calpoly.edu/cgi/viewcontent.cgi?article=1027&context=csse_fac)


[^1]: Maybe it already exists, I did not check yet. <br/> *Update : it does, you can use `nvim('feedkeys', ...)`*
[^2]: Gary Bernhardt talks about this in one of *Destroy All Software* screencasts: [TDD-ing Spikes Away With Rebase](https://www.destroyallsoftware.com/screencasts/catalog/tdding-spikes-away-with-rebase)
