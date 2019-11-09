---
authors: [dmerej]
slug: classes-lie
date: 2019-11-09T19:06:44.665034+00:00
draft: true
title: "Classes lie"
tags: [python]
summary: TODO
---

The lie is: object from the programming world matches objects from real life.

Subject - stolen from exercism.io

```
Manage robot factory settings.

When robots come off the factory floor, they have no name.

The first time you boot them up, a random name is generated in the format
of two uppercase letters followed by three digits, such as RX837 or BC811.

Every once in a while we need to reset a robot to its factory settings,
which means that their name gets wiped. The next time you ask, it will
respond with a new random name.
```

Test:

*(side note: don't write tests like this, please)*

```python
from robot import Robot
def test_everything():
    robot = Robot()

    # Name should be None when robot comes off the factory flow:
    assert robot.name() is None

    robot.start()
    # Started robot should have a name
    first_name = assert robot.name()
    assert first_name is not None
    # ... and its name must follow the pattern
    assert re.match("^[A-Z]{2}\d{3}$", first_name)

    # Name must not change when the robot is re-booted
    robot.stop()
    robot.start()
    assert robot.name() == first_name

    # Name is None when the robot is reset
    # to factory settings
    robot.reset()
    assert robot.name() is None

    # New name is generated when the robot starts
    robot.start()
    assert robot.name() is not None
```

Pretty simple, right?:

```python
import strings
def generate_name():
    first = "".join(random.choice(string.ascii_uppercase) for _ in range (0, 3))
    second = random.randint(0, 1000)
    return f"{first}{second}"

# Side note: I prefer functions like this outside the class,
# but that's a topic for another day

class Robot:
    def __init__(self):
        self._name = None

    def name(self):
        return self._name

    def start(self):
        self._name = generate_name()
        return self._name
```

Now test fails. We need to implement stop(). And the name changes when the
robot is rebooted, so we need to store the 'stopped' state somewhere. Why not a `stopped`  boolean

```
class Robot:
    def __init__(self):
        self._name = None
        self.stopped = True # would be really bad
                            # if the robot was started when
                            # just built ....

    def name(self):
        return self._name

    def start(self):
        self._name = generate_name()
        return self._name
        self.stopped = False

     def stop(self):
        self.stopped = True
```

Congrats! You've model the real world inside your class.

But you've got nothing *close* to solving the bug, and the `stopped` attribute won't help you!


The realy fix is:

```class
class Robot:
    def __init__(self):
        self._name = None

    def name(self):
        return self._name

    def start(self):
        if self._name is None:
            self._name = generate_name()

     def reset(self):
        self._name = None

     def stop(self):
        pass
        # nothing to do here yet - neither
        # the tests nor the spec ask us
        # to have this non-empty
```

The only "physical" stuff the code matches is _the spec itself_, *not* the real world!

And `_name` is just a pile of bytes by the way.





