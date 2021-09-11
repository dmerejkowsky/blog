# Description

This repository contains the sources of https://dmerej.info/blog, built with [hugo](https://gohugo.io/)

Original [theme](https://github.com/MunifTanjim/minimo) by Munif Tanjim.


# Notes for reviewers

You can read the markdown files directly in forge  interface, or follow these steps to see what the actual contents would look like:

* Use `git submodule` to fetch the theme at the correct revision

```
$ git clone git@github.com:dmerejkowsky/blog.git
$ cd blog
$ git submodule update --init
```

* Install [hugo](https://gohugo.io)

* Build a local copy of the blog:

```
$ hugo serve
```

* Done! You can now view the contents on http://127.0.0.1:1313/blog - drafts are shown by default :)
