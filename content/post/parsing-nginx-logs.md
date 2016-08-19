+++
date = "2016-04-10T13:29:51+00:00"
draft = false
title = "Parsing nginx Logs"
+++

This article is a comment on an article I read some time ago.

It's called _Get rid of syslog (or a journald log filter in ~100 lines of
Python)_ and you can go read it
[here](https://tim.siosm.fr/blog/2014/02/24/journald-log-scanner-python)

It contains some advice about how to parse systemd logs, following the very
good principles exposed in [yet another blog post](
http://www.ranum.com/security/computer_security/editorials/dumb), called
_The Six Dumbest Ideas in Computer Security_.

<!--more-->

Here's a short executive summary:

* The target audience is for people who own their own servers, and thus have to
  make sure their machines have not been compromised.

* Instead of trying to enumerate all the possible attacks and build log filters
  for them (That's dumb idea #2), simply enumerate all the "harmless" logs and
  filter them out.

* The blog then goes on about how to do this for `systemd` logs, using the
  Python programming language.

# How to parse nginx logs

Since I own a `nginx` web server and I'm also concerned about security, I tried
to apply the same principles to the access logs I get for anyone who access my
domain.

By default, nginx logs look like this:

```text
# Harmless log:
94.224.234.9 - - [10/Apr/2016:14:49:32 +0200] "GET /tweets/ HTTP/1.1" 200 247 "-" "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"

# Probably someone trying to see if I'm running wordpress (nice try ...)
130.185.155.10 - - [09/Apr/2016:13:14:02 +0200] "GET /wp-login.php HTTP/1.1" 403 570 "-" "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
```

The least you can say is that at first glance it does not look trivial to
separate harmless logs from the rest.

Fortunately, (and as it's often the case) [the answer is in the documentation](
https://www.nginx.com/resources/admin-guide/logging-and-monitoring/)

You can see that `nginx` folks have taken this use case into account:

```nginx
# This example excludes requests with HTTP status codes 2xx (Success) and 3xx (Redirection)

map $status $loggable {
    ~^[23]  0;
    default 1;
}

access_log /path/to/access.log combined if=$loggable;
```



The bad news is that this feature is only available for `nginx >= 1.7.0.`

But wait! There's an other way.

You can made the `nginx` logs much more readable by using something like:

```nginx
log_format machine_readable '$time_local | '
                            '$status | '
                            '$remote_addr | '
                            '$request | '
                            '$http_user_agent | '
                            '$http_referer';

access_log /var/log/nginx/machine_readable.log machine_readable;
```

This makes sure every field in the log message is separated by a pipe (which
seldom occurs in URLs, requests or user agents)

Then I build my own parser in Python, using the fact that the second field is
the status:

```python

for line in lines:
    # ....
    try:
        fields = [x.strip() for x in line.split("|")]
        date, status, ip, request, user_agent, referer = fields
        status_code = int(status)
    except (ValueError, IndexError) as e:
        # Not good, print it!
        print("WARNING: parsing log failed", e)
        print(line)
        continue
    if not harmless(status_code, ip, request, user_agent):
        print(line)

# ....

def harmless(status_code, ip, request, user_agent):
     # ... some checks using ip and user agent ...

    if status_code >= 200 and status_code < 400:
        return True

    # used by nginx
    if status_code == 499:
        return True

    # We've filtered all the goodness:
    return False

```
