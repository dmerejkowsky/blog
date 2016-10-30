+++
slug = "python3-is-awesome"
date = "2016-08-03T20:05:54+02:00"
description = ""
draft = true
tags = []
title = "python3 is awesome"
topics = []

+++

Python2:

max() arg is an empty sequence

Trying to use max((), 0) returns () because Python2 allows
comparison between heterogeneous types :/

Python3:

BIM! New syntax `def max(*args, *, default=Noe)`, and you can
use max_value = max(list, default=0) without fear :)
