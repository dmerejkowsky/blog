# Description

This repository contains the sources of https://dmerej.info/blog, built with [hugo](https://gohugo.io/)

Original [theme](https://github.com/MunifTanjim/minimo) by Munif Tanjim.


# Notes for reviewers

Sometimes posts are pushed as merge request inside this repository.

You can read the markdown files directly in GitHub web interface, or follow these steps to see what the actual contents would look like:

* Install [hugo](https://gohugo.io)
* Checkout the correct theme:

```
$ git clone git@github.com:dmerejkowsky/blog.git
$ cd blog
$ git submodule update --init
```

* Build a local copy of the blog:

```
$ hugo serve
```

* Done! You can now view the contents on http://127.0.0.1:1313/blog
