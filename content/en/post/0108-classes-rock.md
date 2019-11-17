---
authors: [dmerej]
slug: classes-rock
date: 2019-11-16T19:26:27.902842+00:00
draft: false
title: "Classes Rock"
tags: [python]
summary: |
  Are instances and classes the correct way to represent real-world objects? (part 2)
---

This is the second article in a 2-part series of blog posts that examine
the complicated relationships between the real world and object-oriented
code. If you haven't already, you should the first part: [classes suck]({{<
relref "./0107-classes-suck.md" >}}) first.

Let's recap: we used a `Robot` class to implement the
client specifications. It worked well, until we tried to model the
`start` and `stop` methods with a mutable state. We concluded that
blindly using classes (with methods and mutable attributes)
to represent real worlds objects was a mistake.

# Taking a second look at the code

Let's look at the code again (minus the `stop` method),
along with the spec:

> * When robots come off the factory floor, they have no name:

```python
def __init__(self):
    self._name = None
```

> * The first time you boot them up, a random name is generated:

```python
def start(self):
    if self._name is None:
        self._name = generate_name()
```

> * When a robot is reset, its name gets wiped:

```python
def reset(self):
    self._name = None
```


So we *were* modeling real-world objects with our class after all: the mistake
we made was trying to model the *robot*. But using code to model *the specification*
worked!

If you're not convinced, consider this: the `stop()` method is
empty because the specification said *nothing* about what happens when the robot is
stopped.

If the specification said something like *the robot cannot be reset when it is
started*, then using a `stopped` attribute may have been a good idea.

# Encapsulation

So far we talked only about methods and attributes. There's another aspect of
programming with classes I'd like to examine next: the concept of
_encapsulation_, or how to separate "private" implementation and "public"
interface.

Basically, there are some details of a class that matter
to the people who _wrote_ the class but that _users_ of said class should not know about.

What does this have to do with the real world? **Everything!** Let me show you.

## A single line telling a whole story

In Python, to signify to users of a class that an attribute is not part
of the "public" interface, you prefix it with an underscore, like this:

{{< highlight python "hl_lines=3" >}}
class Robot:
    def __init__(self):
        self._name = None
{{< / highlight >}}

By the way, there are already two pieces of information here:

* robot names are empty at first
* the name likely changes over time (otherwise it would probably have been
  passed as a parameter in the constructor)

But that's again about the specification. What does it mean to have `_name` as a private attribute?

## Working in teams

Let's imagine we are writing software inside a big company with several
teams. Reading the specification again, it's clear that the client is
*extremely* worried about robot names: each and every line of the specification
talks about it! Ff there is a bug affecting the robot name, the client is
going to get pissed.

And that's where using _encapsulation_ makes sense: by "hiding" the `name` attribute from the users of the Robot class,
we are actually covering our bases. If someone from an other team writes `robot._name = "something-else"`,
the client will get mad (the robot name no longer has the correct format), but we can  tell him it's not our fault:
the other team should not have broken the encapsulation without asking us first!

# Conclusion

So, which is it? Do classes rock or suck at modeling the real world?

Well, it all depend of what you mean by "the real world". My advice to you is:

* clarify specifications as much as possible
* write code that closely resemble the specification
* use encapsulation when necessary to protect yourself against misuses of your code

When used correctly, classes are a great way to accomplish all of the above, but
they are also easy to misuse.

Finally, let's go back at our original question: "is modeling the real world
in code worth it?".

Well, if it allows you to implement the specifications correctly and makes
things easier for you and your team mates, then yes, it's definitely worth it.

It's hard, but trying and solve this challenge is what I love about programming.

Cheers!
