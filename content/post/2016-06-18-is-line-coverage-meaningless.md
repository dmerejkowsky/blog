+++
slug = "is-line-coverage-meaningless"
date = "2016-06-18T13:24:56+02:00"
description = ""
draft = false
title = "Is Line Coverage Meaningless?"
+++

Today I'd like to share some thoughts about line coverage.

I already talked about this in a [previous post](
{{< ref "post/2016-06-04-my-thoughts-on-why-most-unit-testing-is-waste.md" >}})
but it has been pointed out that I was not very clear, so I'll try
and write a more focused article.

<!--more-->

# What is line coverage?

To answer this question, we first need to clarify a few things.

When you write tests, you usually split your code in two parts:

* The production code, which contains the actual features of your product.
* The test code, which is the code you write to "exercise" the production code.

They are often split in different files or directories.

In the Java world, the layout looks like this:

<pre>

src
  main
    java
      com
        example
          Hello.java
  test
    java
      com
        example
          TestHello.java

</pre>

To measure line coverage, you have to somehow convince the production code
to emit data about which line is executed when the code runs.

In C++ and `gcc` this is done by using the `--coverage` flag, and in Python it's
done by using a third party library called `coverage.py` and using something
like:

```python
import coverage
coverage = coverage.Coverage()
coverage.start()

run_tests()

cov.stop()
cov.report()

```

(Or just: `python -m coverage run_tests.py`)

In any case, the data will be written in some files, and you can
then later use a tool to generate human-readable reports from those.

Of course, all the lines from your test code will be hit, so you should
exclude the test code when computing coverage.

In any case, at the end you should be able to compute the line coverage
by comparing the number of source code lines in your production code
and the number of these lines that were hit while running tests.


# The problem with line coverage

Take for instance the following Python code:

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
an exponential law)

So, using the line coverage to claim things about the
correctness of a program is just plain wrong.

But does this mean measuring line coverage is pointless?

# A refactoring story

Once again, I'll be using my own experience here, maintaining a Python project
for several years, and making releases about once a month.

At the beginning, for version 0.1 to 2.0, I had a line coverage of about 60%.

It clearly meant I did not have enough tests: after each release I had to fix
quite a large amount of bugs.

Then I did a massive refactoring that lasted several months for the 3.0
release.

During this refactoring, I wrote a test framework that made it really easy to
write a lot of functional tests, and the coverage went up to about 80%

After 3.0 was out, I kept adding new features and doing small refactorings, and
I noticed that users reported much fewer bugs. Instead of having big
"show-stoppers" bugs that made users unhappy, I only had a few bugs,
typically from corner cases I did not anticipate.

Lastly, I tried increasing the coverage to reach 100%, and concluded it was not
worth it.

Some of the reasons included:

* The amount of test code I would have to write was very high.
* I would have to change the production code in ways that I
  did not like.
* The test would be too much coupled to the implementation, which means
  I'll have to change them every time I change the code.
* The production code was both trivial and hard to test (for instance,
  running an `SSH` command)

And until I stopped working on the project, I just tried to keep the coverage at
about 80% without worrying too much.

So, my take away here is something like: "60% coverage in not enough, 100% is
too much, and 80% looks good". But again, this is just for one project, so I may
be completely wrong :)

# Usages for line coverage

Recently I've started a new job, and I think I'll keep measuring line coverage
too there.

Why?

Let's say you discover that one of your libraries (let's say `libfoo`) has
80% line coverage, whereas an other one (let's say `libbar`) has only
20%. You can then ask the following questions:

* Should we just write more tests for `libbar`?
* Should we refactor `libbar` so that writing tests is easier?
* Should we develop a new test framework so that testing `libbar` is easier?
* If `libbar` does not change very often, should we simply assume the
  correctness is enough, and think about testing it more only if we have to
  change it?


Also, line coverage can be useful to spot dead code, that is, production code
that will never be executed, and can safely be removed.

# Other coverage measurements

The [Wikipedia page](https://en.wikipedia.org/wiki/Code_coverage) on code
coverage contains many useful information, so go read it :)

You'll learn about other coverage measurements, such as "branch coverage",
"condition coverage", or "parameter value coverage".

# Mutation testing

I'd like to finish with an other test technique I personally never used, but
that I find interesting: "mutation testing".

The idea is simple:

* You change a bit of the production code (for instance, you invert an `if`
  statement): this produces a new version of the production code called a
  "mutant"
* You run the tests: if they still pass, it clearly means there's a code path
  you did not test: the mutant survived. If a test fails, the mutant was killed.

Then you repeat the process and you measure the percentage of killed mutants.

There are a lot of tests frameworks that implement this idea, so if you ever
tried using those, I'd love to hear from you :)
