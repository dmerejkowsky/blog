---
authors: [dmerej]
slug: how-rust-made-me-a-better-python-programmer
date: 2020-02-27T12:19:25.455275+00:00
draft: true
title: "How Rust made me a better Python programmer"
tags: [python, rust]
summary: |
  The benefits of learning a radically different language
  than the one you are used to
---

# Introduction: my learning years

I wrote my first substantial project in Caml Light in 2005.

Afterwards I went to engineering school. Most of the teaching was using Java.

I still remember looking at this code and thinking: wow, this looks
needlessly complicaed [^1] for just printing out a score table

```java
import java.util.HashMap;
import java.util.Map;

public class Hello {
  public static void main(String [] args) {
    System.out.println("Hello, world");
    Map<String, Integer> scores = new HashMap<>();
    scores.put("Alice", 5);
    scores.put("Bob", 4);
    for (Map.Entry<String, Integer> entry : scores.entrySet()) {
        System.out.println(entry.getKey() + " : " + entry.getValue());
    }
  }
}
```

And then I discovered the code had to be compiled to be run, which involved either:
* Using a _huge_ GUI programm called an IDE
* Or running something like:

```console
$ javac Hello.java
$ java -cp . Hello
```

So naturally, I wanted to see what other "scripting" languages were about, and I decided to
take a look at Perl, Ruby and Python.

Now imagine how I fell when I dicovered I could achieve the same result with:

```python
scores = {"Alice": 5, "Bob": 4}
for name, value in scores.items():
    print(name, ":", value)
```

This feld so much easier! I was wondering why on earth you would spend so much time
typing all that code and waiting for the compilation to finish, and deal with the JDK/JRE,
and all that __shtuff__.

# My first job

My first real job involved writing a _lot_ of `C++` and a tiny bit of Python.

I was told that "serious" code was to be written in C++ because of performance,
and I ....



I've been writing Python code for a very long time (almost 10 years). To
this day, it is my favorite language. I feel productive writing it,
I love its ecosystem, its gouvernance, its features, its tooling, its
syntax and everything else.


But I also recognize a few of its shortcomings:

* It's slow
* It has a garbage collector
* It's easy to make a mess - maintaining clean Python code in a big codebase is hard
* It's a bit ackward to write concurrent code in it (but it's definitely possible, in practice
  the GIL is not that big a deal)

For quite a long time I heard the phrase : "You should learn many programming languages", so
I always had this little voice in my head "Your attachement to Python is not rational, you should
try something else and maybe you'll like it!"

# Rust

Almost 2 years ago, I decided to try


[^1]: And by then we did not have the enhanced for loop - I completly forgot what we used back then, to be honest

Actually, I went through Ruby and Perl before falling in love with Python - don't tell anyone
