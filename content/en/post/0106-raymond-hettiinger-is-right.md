---
authors: [dmerej]
slug: raymond-hettiinger-is-right
date: 2019-11-09T18:59:50.826187+00:00
draft: true
title: "Raymond Hettiinger is right"
tags: [python]
summary: |
    TODO
---

Say you are teaching Python and you want to explain methods to newcomers.

Here are the steps

* classes are blue prints
* instances are whhat you get when you use the class
* classes can have attributes, the same way modules do
* functions inside class are called methods and they *must* take `self` as first parameters
* when you call a method, something magic happens with self
* __init__ is a special method that is called magically at instantiation
* Side note: It is called a constructor but it does not "construct" nor "build" anything - sorry about the bad naming  :/

All clear?

Now watch this:

```python
class MyClass:
    def my_method(self):
        pass


my_instance = MyClass()
```

```
>>> my_instance.my_metod()  # note the typo
AttributeError: 'MyClass' object has no attribute 'my_method'
```

And try to explain the error message!

What's an object? Why is Python telling me about a missing *attribute*?

Consider how _much_ understandable the message would be if it was:

```python
>>> my_instance.my_metod()  # note the typo
AttributeError: 'my_instance' instance of class `MyClass` has no method named 'my_method'
```

