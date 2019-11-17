---
authors: [dmerej]
slug: classes-suck
date: 2019-11-09T19:06:44.665034+00:00
draft: false
title: "Classes Suck"
tags: [python]
summary: |
  Are instances and classes the correct way to represent real-world objects?
---

# Introduction

A long time ago I received a lecture about the usage of databases and software design. More specifically, how to translate relationships like "one-to-one", "many-to-many", or "one-to-many" inside databases schemas.

Ten years later, I still remember one thing the teacher said at the beginning of the course:

> When you are designing your database schema, your enemy is the real world. The real world is *always* more complicated than you anticipated.

This is not new, of course, but it raises some interesting questions: how can we model the real world in our code? Is it worth it? Is not all software made of abstract objects? Are classes and instances the correct way to do it?

# A two-part exploration

In these two parts series, we'll try and answer the last question.

We will use an exercise I've stolen from the [exercism.io](https://exercism.io/), website, and the two parts will argue opposing points of view.

Let's start with part one: *classes suck*. Bear in mind there we'll be a part two called *classes rock*, so don't leave angry comments below just yet :)

One last thing: this is a story based on real events: the code I'm about to show below was written this way by students I've just taught about instances and classes in Python.


# The Robot factory exercise

Here are the specifications of the exercise:

> Your are a developer inside a robot factory. Your task is to manage robot settings. Here are the rules:
>
> * When robots come off the factory floor, they have no name.
>
> * The first time you boot them up, a random name is generated in the format
>   of two uppercase letters followed by three digits, such as RX837 or BC811.
>
> * Every once in a while we need to reset a robot to its factory settings,
>   which means that their name gets wiped. The next time you ask, it will
>   respond with a new random name.

And here's the code we're given a starting point:

```python
class Robot:
    # Put your code here:
    pass

def test_name_is_not_set_at_first():
    robot = Robot()
    assert robot.name() is None


def test_started_robots_have_a_name():
    robot = Robot()
    robot.start()
    actual_name = robot.name()
    assert re.match(r"^[A-Z]{2}\d{3}$", actual_name)


def test_name_does_not_change_when_rebooted():
    robot = Robot()
    robot.start()
    name1 = robot.name()

    robot.stop()
    robot.start()
    name2 = robot.name()
    assert name1 == name2


def test_name_changes_after_a_reset():
    robot = Robot()
    robot.start()
    name1 = robot.name()

    robot.stop()
    robot.reset()
    robot.start()
    name2 = robot.name()
    assert name1 != name2
```

Let's try to fix tests one by one, starting with the first one.

# Making the first tests pass

All we need is a `name()` method that returns `None`:

```python
class Robot:
    def name(self):
        return None
```

For the next test, we need a `start` method that will cause the name to change. Let's store the name in a private attribute `_name` and adapt the rest of the code:

```python
def generate_name():
    # implementation omitted for brevity

class Robot:
    def __init__(self):
        self._name = None

    def name(self):
        return self._name

    def start(self):
        self._name = generate_name()
```

To fix the next test, we need to implement `stop`:

```python
def generate_name():
    ...

class Robot:
    def __init__(self):
        self._name = None

    def name(self):
        return self._name

    def start(self):
        self._name = generate_name()

    def stop(self):
        pass
```

And then we get:

```
test_name_does_not_change_when_rebooted:
>       assert name1 == name2
E       AssertionError: assert 'KJ721' == 'JO813'
E         - KJ721
E         + JO813
```

# Making the test about reboot pass - first attempt

Clearly, we have a bug in our implementation. The robot's name must not change when it's rebooted.

If we follow the "code objects must reflect real-world objects" rule, we may be tempted to say that robots have a *state* and that this state can be used to know when the name must be regenerated.

And we can choose to represent the state of the robot with a `stopped` attribute inside the `Robot` class:

```python
class Robot:
    def __init__(self):
        self._name = None
        # Better make sure robots are stopped when
        # they come out of the factory floor :)
        self.stopped =  True

    def name(self):
        return self._name

    def start(self):
        self._name = generate_name()
        self.stopped = False

    def stop(self):
        self.stopped = True
```

And that's where classes have failed us. This `stopped` attribute does not help *at all* making the test pass.

We tried and model the real world in our class but it was useless. And then we realize that there's no so such thing as a "boolean" in the real world. In the real world, robots have LEDs that are turned on or turned off!

# Making the test about reboot pass - second try

Let's revert the change that introduced the `stopped` attribute, and look at the implementation again. It becomes clear that to make the test pass, we just need an if in the `start` method:

{{< highlight python "hl_lines=9-10" >}}
class Robot:
    def __init__(self):
        self._name = None

    def name(self):
        return self._name

    def start(self):
        if self._name is None:
            self._name = generate_name()

    def stop(self):
        pass
{{< / highlight >}}

Making the last test pass is easy: we only need to reset the `._name` attribute when the robot is reset:

```python
class Robot:
    def __init__(self):
        self._name = None

    def name(self):
        return self._name

    def start(self):
        if self._name is None:
            self._name = generate_name()

    def stop(self):
        pass

   def reset(self):
        self._name = None
```

Now all test pass and we're done.

# (Temporary) conclusion

Looking at the code, it looks like our object has nothing to do with the real world. The closest connection with the real world is the `._name` attribute which is probably just a bunch of zeros and ones inside the memory chip of the robot.

Let's face it, using classes to represent the real world is a myth, probably spread by overzealous Java developers, or clueless researchers locked inside their ivory towers.

Or is it? Let's find out in [part two]({{< relref "./0108-classes-rock.md" >}})!.
