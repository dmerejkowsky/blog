---
authors: [dmerej]
slug: classes-rock
date: 2019-11-09T19:26:27.902842+00:00
draft: true
title: "Classes Rock"
tags: [python]
summary: |
  Are instances and classes the correct way to represent real-world objects? (part 2)
---

This is the second article in a 2-part series of blog posts that examine the complicated relationships between the real world and object-oriented code. If you haven't already, you should the first part: [classes suck]({{< relref "./0107-classes-suck.md" >}}) first.

# Taking a second look at the code

Let's look at the code again:

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


# A single line telling a whole story


```python
class Robot:
    def __init__(self):
        self._name = None
```

There's a *ton* of info packed here:

* Names are None by default
* Client is extremly worried about the name
* Name change over time (otherwise it would be passed as parameter
  in `__init__`)
* It's private: if someone from the other teams write `robot._name = "something-else"` the client will get mad but we'll team him it's not our fault - other team should have not do that without asking us first.

So, which is it? Do classes rock or suck at modelling the real world?

* I don't know
* It depends

And _that's_ why programming is hard, folks!

Better conclusion:

* it's worth trying to achieve that
* classes _may_ not be the right way to do it

