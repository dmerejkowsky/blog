---
authors: [dmerej]
slug: tips-from-a-build-farmer-part-2-some-concepts
date: "2018-08-28T18:17:04.151310+00:00"
draft: false
title: "Tips From a Build Farmer - Part 2: Some concepts"
tags: [ci]
summary: ... or the importance of good metaphors
---

_Note: This is part 2 of the [Tips From a Build Farmer]({{< ref "/post/0082-introducing-tips-from-a-build-farmer.md" >}}) series._

In this article we'll define a few concepts that we're going to use in the rest of this series.

But first, let's look at some Java code! [^1]

# Fruits and apples


```java
class Fruit {
  // ...
}

class Apple extends Fruit {
	private final String type;

	public Apple(String type) {
		this.type = type;
	}
}

class Foo {

	void func() {
		List<Fruit> fruitList = new ArrayList<Fruit>();
		Apple golden = new Apple("golden");
		fruitList.add(golden);
	}
}
```

It's clear that the `Apple` class is not really an apple. It's a bunch of data and methods that identifies an apple via a `type` string. We can say that the Apple class is a *metaphor* for the real apple object.

But note that `fruitList` is *not* a list of fruits! It's a slice of memory containing objects of a certain type, and if you forget that, you're about to get nasty compilation failures such as this one:

```
Apple firstFruit = fruitList.get(0);

foo.java:21: error: incompatible types: Fruit cannot be converted to Apple
```

You can solve that with generics of course, but this is not my point.

My point is that as programmers we are surrounded with metaphors all day long, and sometimes without realizing it. After all, all we do is write text that ultimately is converted to a sequence of zeros and ones and ran on a piece of silicon.

We create abstractions and encapsulations to be able to reason about the code we write, and we often do that with metaphors.

We also really care about naming. For instance, you could argue the `type` field of the Apple class should be named `variety` instead, because this word already has several meanings for any developer.

But metaphor are not only used by developers.


# Why you should care

If you read about Agile or XP, you will find out there's a *programming practice* called *System Metaphor*.

It goes with a bunch of other disciplines such as Test Driven Development, Sustainable Peace, and Collective Code Ownership. You can find [the whole list on Wikipedia](https://en.wikipedia.org/wiki/Extreme_programming_practices).

Among programmers we sometimes don't think too much about metaphors because we can still look at the *actual code implementation*  (or comments) to figure out what the name means.

Things change when we need to communicate with people outside the team, such as Product Owners, Marketing or Sales. We use metaphors when we talk to them about features or components of our systems.

Thus, coming up with good metaphors is the only way to communicate effectively between business and tech teams. We have to come up with a *common vocabulary*  that everyone agrees on.

This means, among other things:

* Avoiding using the same word for different things
* Making sure each word means the *same thing* for everyone.

Anyway, this is why I wanted to talk about metaphors. The concepts I'll be listing below can also be used as such to communicate between people both inside and outside your team.

# Concepts

The concepts are listed in a top-bottom manner. So if you encounter a term you don't understand, just keep reading!

## Continuous Integration

*Continuous Integration*, or CI for short, is any situation where there exist *scripts* running on a *build farm*.

## CI Scripts

The *scripts* are usually written in an "scripting language" (hence there name).

They have access to some or all the source code and can do many things: compiling, running some tests, produce deliveries, deploy new servers, and so on [^2].

They can:

  * Run automatically upon certain events (like a merge request being created)
  * Run automatically on specific hours (for instance, everyday at 9 AM)
  * Be triggered by a manual action (like running a separate program or using a Web interface).


## Build Farm

A *build farm* is made of two things. A set of *runners*, and a *coordinator*.

There may be just one runner, and the coordinator may be running on the same machine as the runner, it does not matter; what matters is that runners and coordinators do different things.

## Runner

A runner is any machine on which the scripts run. That's all.

## Coordinator

A coordinator:

  * Listens to the *triggers* listed above,
  * Dispatches the execution of the scripts on one or several machines among the runners,
  * Aggregates the results of those executions. Those can be test reports, logs, files, etc. ...

Note that if you're using Jenkins, the coordinator is called *master*, and the runners are called *nodes* or *slaves*.

## Job

A *job* is a script plus a *configuration*. The configuration contains at least the specifications for the triggers, but may also contain mappings of keys and values.

## Build

A *build* is the execution of a job.

Usually, builds have a *number*, and jobs have a *name*.

P.S: I know that "build" has many other meanings in the programming world, but I don't have a better one.

## Failure and success

Builds have **only one way** to *succeed*, and many ways to *fail*. (The script could not run, the compilation failed, all the tests but one passed, etc. ).


By extension, we say that a job is *failing* when the most recent build failed. We say that the job is *stable* if the last build succeed. Thus a job can *go from stable to failing*, or *be back to stable*.

Jobs can have other states depending on the coordinator such as "skipped", "starting", or "cancelled".

Side note: Jenkins assigns colors to builds, such as "yellow" when the compilation is OK but some tests are failing. For me a yellow build is just an other kind of *failed* build. [^3]

## Notification

When a job reaches a certain state, you may use a *notification* to communicate the event to some humans.

For instance, if a build triggered by a pull request fails, an e-mail may be sent by the coordinator to its author.


## Step

We saw that scripts can do many various tasks. Scripts often go through a series of *steps*, like our example in [CI scripts are scary]({{< ref "/post/0083-tips-from-a-build-farmer-part-1-ci-scripts-are-scary.md" >}}):

* Fetch the code
* Compile everything
* Run the tests
* Generate an archive

Usually a failure in one of the steps causes the script to terminate immediately (but not always).

Also, the series of steps may differ from one job to an other. For instance, you may want the "deploy to production" step to only run for certain triggers :P

## Artifact

An *artifact* is a file produced by one or several steps. Artifacts may be exchanged across jobs, in some cases *via* the coordinator, but other mechanisms may be used.

## Delivery

A *delivery* is an artifact that can be used by your customers. Deliveries are often deployed to a download page.

## Deployment

A *deployment* is a special kind of job that consists in either:

* Uploading some files to a remote location
* Updating some code that is running somewhere else

In the second case you may:

* Upload the source files directly to the server. You may do this for sites written in PHP for instance.
* Run some Ansible Playbooks
* Build and upload a Docker image to a container registry and then ask some nodes in a cluster to use the new docker image
* ... or any other technique

Since deployments are just jobs, they *also* have only one way to succeed and many ways to fail &hellip;

## Environment

An environment is just a group of machines where a certain kind deployment occurs.

For instance, you may decide that:

* Every deployment triggered by a push on the master branch will go to an environment called "pre-production"
* Every deployment triggered by a tag starting with 'v' will go to an environment called "production".

By the way, GitLab CI has an [excellent support for environments](https://docs.gitlab.com/ee/ci/environments.html).

# Conclusion

And that's the vocabulary I will be using. I hope you'll find it useful.

Next time we'll answer the number 1 question: "What programming language should I use to write CI scripts?".

[^1]: You can skip directly to the [concepts section](#concepts) if you want, but I wanted to talk about development practices a little bit.
[^2]: Note that I'm including Continuous Delivery (CD) inside CI. Your mileage may vary.
[^3]: Plus I'm colorblind
