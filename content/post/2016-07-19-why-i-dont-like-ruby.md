+++
slug = "why-i-dont-like-ruby"
date = "2016-07-19T21:21:32+02:00"
description = ""
draft = false
tags = []
title = "Why I Don't Like Ruby"
topics = []

+++

I'm going to compare two programming languages which is something
really silly to do (or is it?)

You should now I've only used Ruby a few times: I followed a `Rails` tutorial
once, and  I also wrote a small web app with [Sinatra](http://www.sinatrarb.com) in about 1500 lines of code. (nice framework, by the way)

On the other hand, I've been writing Python code for several years,
on a project with about 25,000 lines of code.

But I could not resist the temptation, so here goes ...

(there's an other classic troll at the end too, because why not?)

<!--more-->


# Introduction

Since quite some time I've subscribed to the excellent [Ruby Tapas](http://www.rubytapas.com/)
screencasts series, by Avdi Grim.

By the way, you should subscribe too : it's not that expensive, and you'll get
three short videos (5-10 minutes) every week on various topics, not just
Ruby ...

Anyway, I'm going to spoil the episode #427 [Subprocesses part 7: Environmental Isolation](
http://www.rubytapas.com/2016/07/18/episode-427-subprocesses-part-7-environmental-isolation/),
so if you want to have a look, do that first (you'll need a paid subscription,
but as I said, I think it's worth it)

# Controlling sub processes environment
So, in this episode Avdi explains how you can control the environment variables
that a process ran from Ruby will have access to.

## By default behavior

First, if you specify nothing, the whole environment is forwarded to the child
process. This looks the same in Ruby and in Python:

```ruby
# Ruby
system("foo")
```

```python
# Python
subprocess.run("foo")
```


## Adding a new environment variable

Then he explains that if the *first* argument of the `system` call is a hash,
the values will be *added* to the environment:

```ruby
# Ruby
system({"WITH_SPAM" => "true"}, "foo")
```

In Python, the first argument is always the command line to run, (no special
case), so it's more convoluted:

```python
# Python
env = os.environ.copy()
env["WITH_SPAM"] = "true"
subprocess.run("foo", env=env)
```

Note that if you forget the `.copy()`, you'll be modifying the global
environment instead! (that's an other story ...)

So, Ruby wins, right?

Well, that's where I disagree. I believe Ruby is "optimized" for the most usual
case, but things start to go south if you want to do other things.

## Using a clean environment

With Ruby, if you want to start with no environment variable at all, you cannot
just use

```ruby
system({}, "foo")
```

you have to specify an obscure option, like this:

```ruby
system({}, "foo", unsetenv_others: true)
```

In Python, it's quite easy:
```python
subprocess.run("foo", env=dict())
```

You may say: "But, empty dictionaries and None are both falsy in Python, isn't
this confusing?"

Well, not really, because `None` in the `subprocess.run()` API means: "don't do
anything fancy", like `subprocess.run("foo", stdout=None)` means "do not
redirect stdout".

Ditto for timeout: `timeout=0` means the process will get killed after
0 seconds, but `timeout=None` means there's no timeout at all.

See? Consistency!

# Ruby and Python have different philosophies

I'd sum up by stating that the Python API is more easy to grasp and use [^1]
at the cost of being slightly more akward to use is some cases.

I'd also like to point out that the Ruby API is meant to be more "natural" or
"expressive", but at the cost of having a slightly harder to grasp API
(frankly, are you going to remember the `unsetenv_others` keyword?)

So yeah, choosing your programming language really is about a "philosophical"
way of seeing the world, and that's probably why :

- it continues to be the most easy way to start flame wars
- you should invest time finding "your" language or at least understand its
  "philosophy" before starting using it

# Bits and pieces


## Removing variables from the environment

There's at least one use case I know when this is useful: it's when running
`git` commands from a `git` hook.

If you try to run other `git` command in a different repository, you'll notice
it does not work, because the hooks are called with environment variables
like `GIT_WORKTREE` and `GIT_DIR` that take over the working directly.

So you do have to remove them, like so:

```python
env = os.environ.copy()
for key in list(env.keys()):
    if key.startswith("GIT_"):
        del env[key]
subprocess.run("git", "reset", "--hard",
               cwd=repo_path, env=env)
```

## Expanding paths when $HOME is not set


```ruby
# Ruby
ENV.delete("HOME")
File.expand_path("~")
# foo.rb:2:in `expand_path': couldn't find HOME environment -- expanding `~' (ArgumentError)
```

```python
# Python
del os.environ["HOME"]
os.path.expanduser("~")
# no crash, since it parses /etc/passwd to find the home directory
# using the `pwd` module
```

Just sayin' :)

(Maybe it's a deliberate design by the Ruby developers, I don't know)


## Messing up with `cron`

Avdi explains that controlling the environment matters when writing `cron` jobs.

I'd like to say that you really should be using `systemd` timers instead if you
get a chance.

Sure, you'll have to write both a `foo.service` _and_ a `foo.timer` file, but:

1. systemd uses an hard-coded value for `PATH` that should work out of the box,
   so you can keep your `#/bin/env ruby` shebang (See the [documentation](
https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Environment%20variables%20in%20spawned%20processes) for details)

2. You'll be able to set the environment variables directly in the `.service`
   file, or in a file it `/etc/`, using something like

```text
# in foo.service
[Service]
ExecStart=/usr/bin/foo
EnvironmentFile=/etc/default/foo

# in /etc/default/foo
WITH_SPAM=1
```

3. You'll be able to run you "cron" script by calling `systemctl start
   foo.service` and you'll know it will run *exactly* the same way when started
   by the timer.

4. By default, `stdout` will get logged directly to the systemd journal, so you
   don't have to write things like `/usr/bin/foo 2>> /var/log/foo.log`


# Conclusion

That's all folks :) I'd like to take the opportunity to re-affirm my decision to
abide the [Croker's Rules](http://sl4.org/crocker.html), so feel free to tell me
I'm stupid and wrong!

[^1]: Yeah, I know it took the Python community twelve years between the [PEP 324](https://www.python.org/dev/peps/pep-0324/), announcing the `subprocess` module, and the addition of an actually usable `run()` function for Python 3.5 ...
