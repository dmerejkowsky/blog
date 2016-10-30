+++
slug = "pytest-temporary-directories-and-build-farms"
date = "2016-03-31T23:52:39+00:00"
draft = true
title = "pytest, Temporary Directories and Build Farms"
+++

For this post, I'd like to tell a short story that happened to me a while age
while trying to run tests for a project of mine on a buildfarm.

Hopefully you won't redo the same mistakes I did :)

<!--more-->

# The problem

Let's say you have a code base which interact with the filesystem.

Basically you are screwed, because from a testing point of view, the
filesystem is just an ugly global variable, which persists between tests
runs, so you have to find a way to isolate your tests from the
filesystem.

A nice way to work around that is to use temporary directories, using
something like:


```python
class MyTest():

  def setup(self):
    self.tmp  = create_tmp_dir()

  def tearDown(self):
    self.tmp.remove()

  test_one(self):
    # do something with self.tmp

  def test_two(self):
    # do something with a brand new self.tmp
```


This works, but there are some problems:

* When the test fails the temporary directory is cleaned and it's not easy to
  investigate (or you have to create breakpoints and so on)

* You'll get "filesystem leaks" if someone does not have a correct `tearDown`
  function

* On a build farm, bad stuff happens all the time: test scripts crash, jobs are
  interrupted, so in the end you end up with ton of  stuff in `/tmp` you don't
  need.

It's even worse on Windows because `%APPDATA\Local\Temp` is not cleaned when
the machine reboots

# True story: going the py.test way

At first, tests were written using `unittest`

After a while, we rewrote the tests to use [pytest](http://pytest.org)

Tests now look like:

```python
def test_one(tmpdir):
    # do something with tmpdir

def test_two(tmpdir):
    # do something with a brand new tmpdir
```

And then after one week with this on production, we got all the jobs
failing with "No space left on device" errors our farm.

Quick investigation revealed there were no inodes left on `/tmp` [^1]

So we discovered that the default `tmpdir` you get when using `pytest`
does **not** get removed at the end of the test.

## First instinct

My first instinct was "there's probably something wrong in the production code
or in the `conftest.py`", so I quickly wrote a script looking like:

```python
# check-leaks.py
# Make sure the tests do not create filesystem leaks
import tempfile

basedir = tempfile.gettempdir()
before = os.listdir(basedir)

# run the tests

after = os.listdir(basedir)

if before != after:
  sys.exit("Tests leaks some temp dirs")
```

But sure enough, testing with the script on a really basic code, not
using any special `conftest.py`, showed filesystem leaks.

So I went into the `py.test` code base and quickly wrote a patch:

```diff
Subject: [PATCH] clean the freaking tempdir !

---
tmpdir.py | 1 +
1 file changed, 1 insertion(+)

diff --git a/tmpdir.py b/tmpdir.py
index 3907c92..7344120 100644
--- a/tmpdir.py
+++ b/tmpdir.py
` -65,4 +65,5 ` def tmpdir(request):
    name = request.node.name
    name = py.std.re.sub("[\W]", "_", name)
    x = request.config._tmpdirhandler.mktemp(name, numbered=True)
+    request.addfinalizer(x.remove)
    return x
--
```

## Taking a step back

Then I realized there was probably a good reason why the temporary
directories were not removed by default ...

So I took a closer look at the files `py.test` was creating "behind my
back"

<pre>
── pytest-70
│   └── test_warn_on_default_change0
├── pytest-71
│   └── test_warn_on_default_change0
├── pytest-72
│   └── test_call_setup_review0
├── pytest-73
│   ├── test_call_setup_review0
│   ├── test_does_not_store_if_setup_fails0
│   └── test_new_project_under_code_review0
├── pytest-dmerejkowsky -> /tmp/pytest-73/test_new_project_under_code_review0
</pre>

Actually this is very nice!

You've got a new, numbered base directory at each test session, so it's
very easy to inspect what changed between two tests sessions.

All this time wasted inserting break points or messing with the code
just to get those temp dir not removed...

So I realized I should not change the way `pytest` work, and let the
`tempdir` fill up `/tmp`. On a dev box it does not matter, and my
fellow coders will be happy to have those temp dirs available to investigate
test failures.

The only problem left was the buildfarm.

But I already knew the solution!

```python
# run_tests.py
import tempfile

def test_project():

  basedir = tempfile.gettempdir()
  before = os.listdir(basedir)

  # run the tests

  after = os.listdir(basedir)

  for file_name in after:
      if file_name not in before:
          clean(file_name)
```

Note that the code is quite safe because it only cleans directory
created during tests.

It is in fact more generic that I hoped. It does not care how the
temporary directories are created, as long as they end up in
`tempfile.gettempdir()`

So I'm now using the same piece of python code when running our
C++ tests :)

# Lessons learned


* Always start reproducing the problem with the minimum amount of code
  possible. This was the key to not wasting my time looking for a bug in my own
  production code

* Think twice before patching upstream's code!

* When in doubt, take a deep breath and take a step back. Often there's a
  simpler way to do it.

* Finding the generic solution to the correct problem is better than finding a
  hack, aka as "now is better than never, although never is often better than
  *right* now.[^2]

[^1]: Fun fact: when you are out of inodes, `df -h` won't say anything, you have to use
      `df --inodes` to see the problem.

[^2]: Congrats if you recognized the
      [Zen of Python](http://www.python.org/dev/peps/pep-0020/)
