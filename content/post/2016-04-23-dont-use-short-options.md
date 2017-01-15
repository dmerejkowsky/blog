---
slug: "dont-use-short-options"
date: "2016-04-23T14:19:33+00:00"
draft: false
title: "Don't Use Short Options!"
tags: ["misc"]
---

This post tries to show you how and when to use long and short options.

<!--more-->

# What are short options?

Usually, when you are using a program that has a command line interface,
options come in two forms: long and short options.

For instance, if you run `ls --help` you'll see something like:

<pre>
$ ls --help
Usage: ls [OPTION]... [FILE]...
...
  -a, --all                  do not ignore entries starting with .
</pre>

So you have two ways to list all files in the current directory, even when they
start with a dot:

<pre>
$ ls -a
./  ../  .cache  foo/
$ ls --all
./  ../  .cache  foo/
</pre>

Question is: when you should you use the short version, and when you should you
use the long version?

## In documentation

I'm talking about any piece of text that describes a command line to run. It
can be in the documentation of your program when you describe how to use it,
but also in the wiki documentation of your distribution, and so on...

In my opinion, you should always use long options in these occasions.

Let's take an example from the Arch Linux wiki. The issue is to find out if any
of the installed packages have disappeared from AUR
(AUR is the Arch Linux User Repository, and sometimes, packages disappeared
during the transition from AUR3 to AUR4.)

The solution is to ask `pacman` (Arch Linux package manager) for any "foreign"
packages, and query the AUR to see if we have
a `200` status code.

* Here's what the command looks like with short options:

```bash
for pkg in $(pacman -Qqm); do
     if ! curl -sILfo /dev/null -w '%{http_code}' \
          "https://aur.archlinux.org/packages/$pkg" \
               | grep -q '^2'; then
       echo "$pkg is missing!"
    fi
done
```

* Here's what the command looks like with long options:

```bash
for pkg in $(pacman --query --quiet --foreign); do
    if ! curl --silent --location --fail \
              --output /dev/null \
              --write-out '%{http_code}' \
         "https://aur.archlinux.org/packages/$pkg" \
             | grep --quiet '^2'; then
        echo "$pkg is missing!"
    fi
done
```

I hope you'll agree that the version with long options is easier to understand.

It does not really matter that the command is longer, people are going to
copy/paste the entire block anyway.


# In scripts


If you're writing a script that use an external command line program to do the
job, you probably always want to use
long options too. Here's what it looks like in Python:

* With short options:

```python
cmd = ["rsync", "-rlptc", "--special", "--progress",
             "--exclude=.debug"]
subprocess.call(cmd)
```

* With long options:

```python
cmd = ["rsync",
    "--recursive",
    "--links",
    "--perms",
    "--times",
    "--specials",
    "--progress", # print a progress bar
    "--checksum", # verify checksum instead
                           # of size and date
    "--exclude=.debug/", # exclude debug symbols
]
subprocess.check_call(cmd)
```

Note how in the short version we have a string that makes absolutely no sense
to the reader: `rlptc`, unless he knows the man page of `rsync` by heart.

Also note that having one (long) option per line has at least two advantages:

* If we do a commit that adds or removes options, the patch will be easier to
  read
* We can write descriptive comments explaining what each option we use is for


# In a command line prompt

I also think you should also use **long** options when typing commands in your
shell.

Don't believe me? Let me tell you a story.

For quite a long time I tried to remember `rsync` short options, and I never
managed to do it...

Is there a `-v` for verbose? I know there's `-r` for recursive, but is `-p` for
progress or for preserving permissions? And how do I itemize changes or use
checksums?

So every time I had to use `rsync` I had to open the man page.

Then I tried remembering the long options instead. Guess what? They are
**much** easier to remember :)

Recursive is `--recursive`, progress is `--progress`, itemize changes is
`--itemize-changes` and checksums is `--checksum`.

If you're worried you're going to spend more time typing commands I've got two
answers for you: auto-completion and history.

For instance, in my `zsh` setup:

* I type `rsync --pr` then `<tab>` and I have the option expanded for me

* I type `rsync` followed by the `up` arrow key and I can see all the previous
  commands starting with `rsync`

# Conclusion

## For command line users

Short options are good for programs you use from the command line, providing:

* you use them often
* you always use them with the same options
* you want to be able to combine short options, and the combination is easy to
  remember (For instance `ps aux`, `netstat -nutelap`, ...)

For anything else, use long options!

## For writers of command line programs

Make sure to provide both long and short versions of the options your users are
most likely to use.

In Python, you can use
[argparse](https://docs.python.org/3/library/argparse.html),
[docopt](https://pypi.python.org/pypi/docopt), or
[click](http://click.pocoo.org) for this.

But for rarely used options, don't bother finding an obscure shortcut that your
users are never going to remember anyway.
