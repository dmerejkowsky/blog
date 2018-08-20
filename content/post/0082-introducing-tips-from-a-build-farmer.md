---
authors: [dmerej]
slug: introducing-tips-from-a-build-farmer
date: 2018-08-18T08:34:50.667783+00:00
draft: true
title: 'Introducing "Tips From a Build Farmer"'
tags: [ci]
summary: Introducing a new series about CI
---

# Introduction

I've spent several years working on CI scripts and infrastructure. I've used many tools (Jenkins, Travis, GitLab CI, ...). I've made a lot of mistakes, and I learned a few things I thought I might share here.

But let's start at the beginning.

# What is CI?

You probably know that CI stands for "Continuous Integration".

But what does it really means mean to "use continuous integration" for a group of developers working on some source code?

To answer this question, let me define a few terms.

First, there exist some *scripts*. Those are pieces of code which usually have access to some part of the source code. They can do many things like compile some code, run some tests, produce deliveries and so on ...[^1]


Second, those scripts can:

  * Run automatically upon certain events (like a merge request being created)
  * Run automatically on specific hours (for instance, everyday at 9 AM)
  * Be triggered by a manual action (like running a separate program or using a Web interface).

Third, a *build farm* is used. A build farm is made of two things:

* A set of *runners* on which the scrips run,
* A *coordinator*.

The coordinator:

  * Listens to the *triggers* we listed above
  * Dispatches the execution of the scripts on one or several machines among the runners,
  * Aggregates the results of those executions. Those can be test reports, logs, files and so on.

# A new series

That's enough definitions for today :).

The topic of CI is *huge*, so as I did for *[Let's Build Chuck Norris!]({{< ref "post/0060-introducing-the-chuck-norris-project.md" >}})* and *[Quantum of Ideas]({{< ref "post/0057-introducing-quantom-of-ideas.md" >}})*, I'll be writing several articles in the following weeks.

Stay tuned for the first part: [CI scripts are scary]({{< ref "post/0083-tips-from-a-build-farmer-part-1-ci-scripts-are-scary.md" >}}).


[^1]: If you've already heard about Continuous Deployment (CD), note that I'm including it into my definition of CI.
[^2]: If you've already used Jenkins, the coordinator is called *master*, and runners are called *slaves* or *nodes*. This series is not specific to Jenkins, though, so I prefer using a different terminology.
