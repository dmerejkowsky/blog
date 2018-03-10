---
authors: [dmerej]
slug: "meaningful-variable-names"
date: "2016-08-27T14:49:37+02:00"
draft: false
title: "Meaningful Variable Names and the Boy Scout Rule"
tags: ["misc"]
---

Quick! What's the bug fixed by this commit?

```diff
-def compare_links(a_html, b_html):
-    a_soup = bs4.BeautifulSoup(a_html, "lxml")
-    b_soup = bs4.BeautifulSoup(b_html, "lxml")
+def compare_links(local_html, remote_html):
+    local_soup = bs4.BeautifulSoup(local_html, "lxml")
+    remote_soup = bs4.BeautifulSoup(remote_html, "lxml")

-    a_links = set(a_soup.find_all("a"))
-    b_links = set(b_soup.find_all("a"))
+    local_links = set(local_soup.find_all("a"))
+    remote_links = set(remote_soup.find_all("a"))

-    old_hrefs = [x.attrs["href"] for x in a_links]
+    old_hrefs = [x.attrs["href"] for x in remote_links]

-    new_links = [x for x in a_links if x.attrs["href"] not in old_hrefs]
+    new_links = [x for x in local_links if x.attrs["href"] not in old_hrefs]
```

Not that obvious, right?

Please read on to find out how this bug could never had happened,
and how this commit should never have been made.


<!--more-->

# Context

The above is a real commit I made recently.

It's a script I use to automatically tweet about new links, like
[here](https://twitter.com/d_merej/status/768229199551328256)

The first version of the algorithm was quite simple:

* Generate a new version of the blog locally. I use [hugo](http://gohugo.io/)
  for this, meaning the `links.html` page is generated from a
  `links.md` markdown file
* Fetch the remote `links.html` page from `dmerej.info`
* Compare the two html files to find new links
* Generate a new tweet for each new link
* `rsync` the newly generated `links.html` to the remote server

That's where the `compare_links` function is used:

```python
import requests

def main():
    build_blog()

    local_links_path = os.path.join(BLOG_SRC_PATH, "public",
                                    "pages", "links", "index.html")
    with open(local_links_path, "r") as fp:
        local_links_html = fp.read()

    remote_links_html = requests.get("https://dmerej.info/links.html").text

    new_links = compare_links(local_links_html, remote_links_html)
    if not new_links:
        return

    tweet_new_links(new_links)
```

In the first version I was just comparing two html files, so I named
the parameters with `a_` and `b_` prefixes:


```python
def compare_links(a_html, b_html):
      a_soup = bs4.BeautifulSoup(a_html, "lxml")
      b_soup = bs4.BeautifulSoup(b_html, "lxml")

      a_links = set(a_soup.find_all("a"))
      b_links = set(b_soup.find_all("a"))

      new_links = a_links - b_links
      return new_links
```

Simple enough, right?

# A new feature

I was happy with this for a while, until I made a change in the _description_ of
a link:

```diff
--- a/content/pages/links.md
+++ b/content/pages/links.md

- [First description](http://example.com/website)
+ [Second description](http://example.com/website)
```

This caused my script to tweet about `http://example.com/website` twice!

I thought: "OK, the fix is simple: instead of intersecting the two lists
(old and new), build a new list containing all the links which URLs are not in
the old list of links"

So this is the patch I made:

```diff

-    new_links = a_links - b_links
+    old_hrefs = [x.attrs["href"] for x in a_links]
+
+    new_links = [x for x in a_links if x.attrs["href"] not in old_hrefs]
```

Found the bug yet?

# Meaningful variable names for the win!

Let me help you: instead of trying to fix the bug directly, let us think about
the variable names for a moment.

The name with `a_` and `b_` prefixes suggest that the variables can be swapped,
and it's not obvious that `a_` refers to the "local" links, i.e the new ones
that we just added to the `links.md` files, and `b_` refers to the "remote" links,
i.e the one we just fetched from `dmerej.info`.

Let's re-write the function to use meaningful names instead:

```python
def compare_links(local_html, remote_html):
    local_soup = bs4.BeautifulSoup(local_html, "lxml")
    remote_soup = bs4.BeautifulSoup(remote_html, "lxml")

    local_links = set(local_soup.find_all("a"))
    remote_links = set(remote_soup.find_all("a"))

    new_links = local_links - remote_links

    return new_links
```

Then when we want to re-do the patch, we naturally write:

```diff
-    new_links = a_links - b_links
+    old_hrefs = [x.attrs["href"] for x in old_ref]
+
+    new_links = [x for x in new_links if x.attrs["href"] not in old_hrefs]
+    retur new_links
```

I hope that by now you found the bug. Instead of using the `a_links` list
to create the list of new links, we should have used the `b_links` list,
but the mistake was not obvious to spot because of the bad naming.

# The Boy Scout Rule

This rule comes from an [old article](
http://programmer.97things.oreilly.com/wiki/index.php/The_Boy_Scout_Rule)
from our friend Uncle Bob.

Paraphrasing a little bit, it says:

> Always push a cleaner code than the one you pulled.

Have I followed this rule, I would have first made a commit to fix the
variable names *before* changing the code to introduce a new feature, and then
the bug would not have happened.

Instead I was lazy, so I introduced a bug, and the commit that fixes it
is not obvious to read.

(At this point it does not really matter because I'm the only one writing this
code, but still ...)

# Lessons learned

* Meaningful variable names _do_ matter
* If you follow the boy scout rule, make sure to separate the commits that
  simply refactor the code from the commits that actually fix bugs or introduce
  new commits, to have a more readable history.

That's all for today, see you soon!
