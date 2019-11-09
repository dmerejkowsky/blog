---
authors: [dmerej]
slug: classes-rock
date: 2019-11-09T19:26:27.902842+00:00
draft: true
title: "Classes Rock"
tags: [python]
---

Let's go back to the spec:

Notice this just one line:

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

