---
slug: lessons-learned-from-a-failed-pull-request
date: 2017-06-21T17:01:45.570165+00:00
draft: false
title: Lessons Learned From A Failed Pull Request
tags: ['python']
summary: |
         How I failed to make my first contribution to the Python programming
         language, and what I learned from it.
---

# Intro: The netrc file

_If you already know all about the `~/.netrc` file, feel free to skip directly
to the [next section](#the-bug)_


But for those who don't let's take a closer look at the filename and see if we
can find any clues.

1. It starts with `net`, so probably something about the network.
2. It ends with `rc`, which usually stands for "runtime configuration".
3. The path starts with a tilde, which is how UNIX people refer to the home
   directory. So we are probably not looking at something that is supposed to be
   used on Windows.
4. It starts with a dot, which means it's supposed to be "hidden". [^1]
5. It is a configuration file in the home directory, but not in
   `~/.config/`, which means it does not follow the [XDG Base Directory
   Specification](https://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html),
   and thus is probably something a bit old.


I'm not sure how many application rely on the `~/.netrc` file. What I do know is
that many command-line FTP clients (which is not exactly top notch technology, I
know) use this file.

On my latest macOS machine, there's a `ftp` binary and I'm still able to use it:

```console
$ ftp
ftp> open mirrors.kernel.org
Trying 2620:3:c000:b::1994:3:14...
Connected to mirrors.pdx.kernel.org.
220 Welcome to mirrors.kernel.org.
Name (mirrors.kernel.org:dmerej): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp>
```

Notice how I have to provide a username and password even if I only need
anonymous access.

The `~/.netrc` file allows me to not have to type my username and password for
each connection.

I just need to add a line[^2] looking like this in the `~/.netrc` file:

```text
machine mirrors.kernel.com login dmerej password p4ssw0rd
```



# The bug

So, what does this have to do with Python?

Well, in the Python standard library, (stdlib for short) there's a module
dedicated to parse the `~/.netrc` format. The parsing itself is kind of
non-trivial. (See the gory details in the [GNU documentation](
https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html))

Here's how to use it:

```python
import netrc

nrc = netrc.netrc()
login, account, password = nrc.authenticators("example.com")
```

(The `account` is an "additional account password", but I never had to use it)

Anyway, a few months ago I was preparing new machines for doing continuous
integration at work.

(We do cross-platform C++ code on Linux, macOS, and Windows)

I decided to use Python for the build scripts, and I needed to store some access token on
the nodes.

Since the capabilities granted by the token were quite limited, I did not mind
having them in clear text on the nodes themselves, so I decided to use the
`netrc` module.

But on Windows, when running the script directly from `cmd.exe`, the
code crashed with:

```text
Could not find .netrc: $HOME is not set
```

It's not that surprising: `~/.netrc` is a UNIX thing, so it makes sense it
tries using the `$HOME` environment variable, which on UNIX, is almost always
set.

# The "fix"

I happen to know[^3] that in the Python stdlib, there is a function called
`os.path.expanduser` that works very well, even on Windows, and even when `HOME`
is not set.

So I quickly wrote a patch:

```diff
  def __init__(self, file=None):
         default_netrc = file is None
         if file is None:
-            try:
-                file = os.path.join(os.environ['HOME'], ".netrc")
-            except KeyError:
-                raise OSError("Could not find .netrc: $HOME is not set") from None
+            file = os.path.join(os.path.expanduser("~"), ".netrc")
         self.hosts = {}
         self.macros = {}
         with open(file) as fp:
```

and I opened my very first [pull request for Python](https://github.com/python/cpython/pull/123)

# Trying to get the pull request approved

The process took quite a long time, and the pull request is still not accepted.

For me it was obvious at first that the patch was an improvement. I was
re-using existing code, and I did fixed a crash!

But it turned out I had to:

* Write some tests
* Patch the documentation
* Patch the release notes

Let's be clear, I'm not complaining about this, and I'm not blaming the Python
maintainers.

I've always cared about testing very much, and I loved how the Python
documentation is so accurate, and how the change logs are detailed and precise,
and I realize that such requests from the maintainers are required to maintain
this level of quality users of the stdlib love so much.

But trying to make the pull request accepted lead me to a new realization:

**Sometimes, implementation does not matter.**

# Implementation does not matter

It turns out that the _implementation_ of the Python stdlib is somewhat
special.

That's because of how this code is _used_.

People have expectations about it, mostly the fact that the code
that uses it is almost always *retro-compatible*.

The patch I wrote changes the behavior of the stdlib, and for dubious reasons.

If the `~/.netrc` file is a UNIX thing, it makes sense that the `$HOME` variable
will have to be set anyway for the rest of the tools to work. (`ssh` comes to mind).

Also, the `netrc()` constructor accepts path as parameter, so the "fix" can be
written like this:

```python
netrc_path = os.path.expanduser("~/.netrc")
nrc = netrc.netcr(file=netrc_path)
```

Last but not least, the consequences of the patch are hard to describe and can
even lead to breakage.

Consider this code, and assume that `~/.netrc` does _not_ exist and `$HOME` is
_not_ set.

```python

try:
    nrc = netrc.netrc()
except OSError as error:
    # do something with error.args

```

In the old version, `error` would be a `OSError` with one argument (the "$HOME
is not set" message), but with the new version, the code would instead raise a
`FileNotFound` which is a subclass of `OSError`, but with two arguments (the
`errno` and the `filename`)

This could lead to very nasty bugs being introduced.

True, this really is a corner case, but the fact that the _change in
behavior_ is so hard to describe is a good indication that maybe it's not worth
it at all.

# Going further

I'm not sure what's next. There are still requests for changes being made, but I'm
no longer sure the pull request is a good idea. If you have an opinion on this,
I'll be glad to hear it!

Also, I invite you to watch the [Request Under the
Hood](https://www.youtube.com/watch?v=ptbCIvve6-k) presentation from PyCon 2017
which is about a similar topic.


[^1]: There's a nice [story](https://plus.google.com/+RobPikeTheHuman/posts/R58WgWwN9jp) by Rob Pike about this topic.
[^2]: Yes, the password is in clear text, but that's another topic.
[^3]: I know it because of [this other article]({{< ref "post/2016-07-19-why-i-dont-like-ruby.md" >}}) I wrote
