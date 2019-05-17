---
authors: [dmerej]
slug: syntax-does-not-matter
date: 2019-04-27T13:40:16.644249+00:00
draft: true
title: "Syntax does not matter"
tags: [misc]
---

... or at least, not as much as you think.

<!--more-->

# Introduction

We programmers just *love* arguing about programming langages.

Which is the best tool for the job? Which has a future? Which should we be using when teaching programming? Which should be the next Javascript, the next C++, the next SmallTalk

And when we discuss programming langage, we *always* talk about syntax.

Look how clean this code is:

```python
under_age = [x for x in people if x.arg <= 18 ]
```

```rust
let under_age: Vec<_> = people.iter().filter(|x| x.age() <= 18).collect();
```

```ruby
under_age = people.filter { |x| x.age <= 18 }
```
