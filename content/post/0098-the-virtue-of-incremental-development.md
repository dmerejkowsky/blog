---
authors: [dmerej]
slug: the-virtue-of-incremental-development
date: 2019-04-21T12:10:49.553858+00:00
draft: true
title: "The virtue of incremental development"
tags: [misc]
---

Here's today challenge: can you write a command-line tool that
allows to convert from various measurements units?

For instance, you could input "3 miles in meters" and get
"4828.03".

I submitted this challenge to my Python students yesterday,
asking them to write the code from scratch. [^1]


1 hour later, something miracolous happened that I never
would have expect.

But let me tell you the full story.

<!--more-->

# Getting started

I told the students that they could start by writing some "exploratory code".

"Just hard-code anything you have to and keep everything in the `main()` function ", I said.

After a few discussions, we agreed to only write code that converted kilometers to miles, and that
we'll read the value from the command line.

Here's what they came up with:

```python
import sys


def main():
    kilometers = float(sys.argv)
    miles = kilometers / 1.609
    print(f"{.2f}", miles)

if __name__ == "__main__":
    main()
```

I then pointed out that the code was not generic. Indeed, "kilometers", "miles" and "1.609" are hard-coded there.

# Naming a new function

The students understood there was a three-parameters function hiding behind the name. So we went to the drawing board
and after a while we decided to have a function called `convert(value, unit_in, unit_out)`.

Note that we did *not* make any assumption about the *body* of the function. We just wanted to see how `main()` could become
more generic, and we were still allowed to hard-code parts of the code:

```python
def convert(value, unit_in, unit_out):
    coefficient = 1 / 1.609
    result = value * coefficient
    return result


def main():
    value = float(sys.argv[1])
    unit_in = sys.argv[2]
    unit_out = sys.argv[3]

    result = convert(value, unit_in, unit_out)
    print(f"{.2f}", result)
```

Some notes:

* The `main()` function is now completely *generic*, and we probably won't need to change it.
* Also, note how the signature of the `convert` function almost dictated the command-line syntax:

```python
def convert(value, unit_in, unit_out):
    ...
```

```bash
# Usage: 'convert.py value unit_in unit_out
$ python3 convert.py 2 meters miles
```

# Computing the coefficient

Now it was time to get rid of the hard-coded coefficient. This time finding a function name was easier:

```python
def get_coefficient(unit_in, unit_out):
   ...
```

Then we tried to figure out how to implement it. We knew we would be needing a dictionary, but the structure of it was
unknown.

"Back to the drawing board", I said. "Let's write down what the dictionary should look like".

Here's our first attempt:

```python
units =  {
   "km": { "miles": 1/1.609, "meters": 1/1000, ....},
   "yards": { "miles": 1/1760, "meters": ..., "km": ...}
   ...
}
```

"This won't do", I said. "Look at what happens if we add a new measurement unit, such as `feet`".

We'll have to:

* Add a new 'feet' key to the `units` dictionary
* Compute all the coffecient to convert `feet` to all the other units.
* Add a `feet` key to all the other dictionaries

There has to be a better way!

After a short brainstorming session, we decided to limit ourselves to the distance measurement, and to always convert to SI units first.

So we draw the new structure of the `units` dictionary:

```python
# Coefficents convert from "meters"
distances = {
    "km": 1/1000,
    "yards": 1.094,
    "miles": 1/1609,
}
```

And then we thought about the algorithm. We found three possibilities:

* If we want to convert *from meters*, we just have to look up the coefficient in the dictionary
* If we want to convert *to meters*, we can look up the coefficient in the dictionary and return its inverse
* Otherwise, we combine the above two processess and return the product of the two coefficients.


"This is looking good", I said. "Let's try to implement the algorithm but just for the first case and see what happens".

# Testing the algorithm

I showed my students how they could use Python's interpreter to check the get_coefficient() function was working properly.

We quickly manage to get the first case working:

```python
def get_coefficient(unit_in, unit_out):
    # FIXME: only works with distances for now
    # Coefficents to convert from "meters"
    distances = {
        "km": 1/1000,
        "yards": 1.094,
        "miles": 1/1609,
    }
    if unit_in == "m":
        return distances[unit_out]
```

```python
>>> import conversion
>>> conversion.get_coefficient("m", "km")
0.001
>>> conversion.get_coefficient("m", "yards")
1.094
```

"Cool, this works", I said. "Let's see what happens when the input value is not in meters:"

```python
def get_coefficient(unit_in, unit_out):
    # FIXME: only works with distances for now
    # Coefficents to convert from "meters"
    distances = {
        "km": 1/1000,
        "yards": 1.094,
        "miles": 1/1609,
    }
    if unit_in == "m":
        return distances[unit_out]
    else:
        reciprocal_coefficient = 1 / distances[unit_in]
        return reciprocal_coefficient * distances[unit_out]
```

```python
>>> import conversion
>>> conversion.get_coefficient("miles", "yards")
1760
```

"Look how clean the code is", I said. "We have a value that's called `reciprocal_coefficient` and we get it by calling 1 over something else. Isn't this nice?".

# The miracle

I then pointed out that the ['else' after the return]({{< ref "/post/0077-else-after-return-yea-or-nay.md" >}}) was unecessary.


```python
def get_coefficient(unit_in, unit_out):
    # FIXME: only works with distances for now
    # Coefficents to convert from "meters"
    distances = {
        "km": 1/1000,
        "yards": 1.094,
        "miles": 1/1609,
    }
    if unit_in == "m":
        return distances[unit_out]
    reciprocal_coefficient = 1 / distances[unit_in]
    return reciprocal_coefficient * distances[unit_out]
```

And then it happened. "Hey", one of students said, "what if we added meters in the distances dictionary with `1` as value?
We could get rid of the first `if` too!".

"Let's do it", I said:

```python
def get_coefficient(unit_in, unit_out):
    # FIXME: only works with distances for now
    distances = {
        "m": 1,
        "km": 1/1000,
        "yards": 1.094,
        "miles": 1/1609,
    }
    reciprocal_coefficient = 1 / distances[unit_in]
    return reciprocal_coefficient * distances[unit_out]
```

```python
>>> import conversion
>>> conversion.get_coefficient("m", "m")
1
>>> conversion.get_coefficient("km", "m")
1000
>>> conversion.get_coefficient("m", "yards")
1760
```

And of course, this works. When `meters` is either `unit_in` or `unit_out`, all operations will involve multiplying or dividing by 1.

That was a real nice suprise for several reasons:

* One, when I thought about the problem alone, before starting the workshop, I was pretty sure I would need a much more complex data structure.
* Two, one of the students just refused to believe the code would work, even after having seen in work from the interpreter ;)


# Lessons learned

We found a beautiful algorithm and a nice data structure, not by trying to solve *everything* at once, but by slowly building up more and more generic code, getting rid of hard-coded values one after the other, and by carefully thinking about function *names* and *parameters*.

I hope you find this approach useful, and I highly suggest you try using it next time you implement a new feature.

Cheers!




[^1]: I'm using [mob programming](https://en.wikipedia.org/wiki/Mob_programming) during my Python classes. It works really well.
