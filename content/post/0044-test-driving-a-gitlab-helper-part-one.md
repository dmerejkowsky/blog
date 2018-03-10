---
authors: [dmerej]
slug: test-driving-a-gitlab-helper-part-one
date: 2017-06-25T12:06:44.510819+00:00
draft: true
title: Test Driving a GitLab Helper, Part One
tags: ['python', 'test']
summary: |
         How to use TDD when writing a command line tool
         using the GitLab web API, part one.

---

# Introduction

This is not just a little example, it's based on what actually happened
when I spent a few days adding this very feature to a tool we use internally at
work.

In a way, you could say this post is "based on actual events" ;)

But don't worry, we are going to start from scratch so that it's easier to
follow.

We _are_ going to use TDD "the right way", but in a few occasions we'll take
some shortcuts. This is real, remember?


## What we want

We want a command line tool which can be run from a git repository cloned from
GitLab.

When invoked, the tool should:

 * Find the current branch
 * Create a merge request from the current branch, unless it already exists

Additionally, there should be command-line flags allowing to:

* Target any branch for the merge request (not just `master`)
* Assign a member of the team to the merge request.

## Tools

We're going to use `python3` with:

* The `request` library to perform the web API calls
* The `argparse` library to parse command-line option
* `pytest` for testing

{{< note >}}
We could have use [gitlab](https://github.com/python-gitlab/python-gitlab) but
depending on requests alone is good enough for now.
{{< /note >}}


# First steps

## Initial skeleton

```text
$ tree gl-push
.
├── setup.py
├── gl_push
│   └── __init__.py
├── requirements.txt
├── test_requirements.txt
├── test
    └── test_gl_push.py
```

```python
# setup.py
from setuptools import setup, find_packages

setup(name="gl-push",
      version="0.1",
      packages=find_packages(),
      install_requires=["requests"],
)
```

Note how:

* We use `setuptools.find_packages()` to avoid hard-coding the package names


## First test

We start by writing a failing test as usual:

```python
import gl_push


def test_zero():
    gl_push.main()
```

It fails with:

```text
AttributeError: module 'gl_push' has no attribute 'main'
```

We _could_ make it pass by writing a `main()` function in the `__init__.py`, but
I prefer having a separate module for that.

That being said, having to type `gl_push.main.main()` is a bit awkward.

The solution is to import `gl_push.main` from `gl_push/__init__.py`, like so:

```python
# in gl_push/main.py
def main():
        pass

# in gl_push/__init__.py
from .main import main
```

And thus our first test passes!

# The spike

Now we are going to write some code without thinking at all about the quality of
the code or how we are going to test it.

Our goal is to make sure we can do what we need with the GitLab API.

In order to keep things simple, we are going to create a branch new account on
GitLab.com.

First, we create a repository called `dmerej/hello`, with two branches,
`master` and `test1`, on gitlab.com.


Then, we fetch our API token.


So that we don't have to hard-code it in our source code, we use
the `~/.netrc` file:

```
machine gitlab.com login d.merej@gmail.com password p4ssw0rd
```


Now we are ready to write some code!

After browsing the documentation, this is what we come up with:

```python
import requests
import netrc

nrc = netrc.netrc()
_, _, token = nrc.authenticators("gitlab.com")

response = requests.get("https://gitlab.com/api/v4/projects",
                        headers={"PRIVATE-TOKEN": token},
                        data={"owned": True})
print(response.json())
```

This returns a bunch of info about the project we just created,
so that seems to work.

Let's move on and try to create a merge request.

The [doc](https://docs.gitlab.com/ce/api/README.html#namespaced-path-encoding)
says we need to URL-encode the project name, so let's do that.

We use an empty `safe` list when calling `urllib.parse.quote` to make sure
the `/` is replaced by `%2F`:

```python
project_name = "dmerej/hello"
project_id = urllib.parse.quote(project_name, safe=[])


url = "https://gitlab.com/api/v4/projects/%s/merge_requests" % project_id
response = requests.post(url, headers={"PRIVATE-TOKEN": token},
                         data={
                               "id": project_id,
                               "source_branch": "test1",
                               "target_branch": "master",
                               "title": "test1",
                        })
response.raise_for_status()
print(response.json())
```

# Back to TDD


Now it's time to go back to TDD.

Since we don't want to hit the GitLab API everytime we run a test,
we're going to use mocks.

We are also going to perform actual `git` calls in the production code, so
how are we going to test that?

## The GitServer

For the git calls, it's best to use actual files on the filesystem, and actual
calls to the `git` commands.

We could try to mock all that, but it's difficult and could be tricky to debug.

If everything happens on disk, it's also easy to debug problems.

So we are going to use files in a temporary folder (so that tests stay
isolated).

Thus, we decide to write a class called `GitServer` that we'll be able to use
for testing.

And since this will be a critical piece of our tests, we're going to use TDD to
write it :)

Very meta, I know, but consider the horror if we have bugs or bad code in this
class!


First, let's make sure we can create a repo and then clone it.
We are using the built-in `tmpdir` and `monkeypatch` fixture of `pytest`.

`tmpdir` will be a unique temporary directory for each  test,
and `monkeypatch.chdir()` will change the working directory, but just for
the duration of the test:

```python
import gl_push.git
from gl_push.test.git_server import GitServer


def test_can_create_a_repo(tmpdir, monkeypath):
    server = GitServer(tmpdir)
    url = server.create_repo("foo")
    monkeypath.chdir(tmpdir)
    gl_push.git.run("clone", url)
```

Note how we creates API "out of the blue", such as the `GitServer`
initialization, and the call to `gl_push.git.run()`.

We know this API is nice because the test "reads well".

Here what happens while we try to make the test pas, each
error message we get from `pytest` followed by the change in the code.

You'll see that the changes stay very small for quite some time, but that
we still gain quite a lot of features.



`ModuleNotFoundError: No module named 'gl_push.git'`

Create file `gl_push/git.py`

<hr />

`ModuleNotFoundError: No module named 'gl_push.test.git_server'`

Create file `gl_push/test/git_server.py`

<hr />

`ImportError: cannot import name 'GitServer'`
```python
class GitServer:
    pass
```

<hr />

`TypeError: object() takes no parameters`
```python
class GitServer:
    def __init__(self, tmpdir):
        self.tmpdir = tmpdir
```

<hr />

```text
AttributeError: 'GitServer' object has no attribute 'create_repo'
```

```python
class GitServer:
    def __init__(self, tmpdir):
        self.tmpdir = tmpdir

    def create_repo(self, name):
        pass
```

<hr />

```text
AttributeError: module 'gl_push.git' has no attribute 'run'
```

```python
# in gl_push/git.py

def run(path, *cmd):
    pass
```

<hr />

And then the test passes.


Note that we did nothing but create empty functions.

We could write some test to make sure `run()` actually does something, but

1. The implementation is going to be _really_ simple
2. If we _do_ have a bug in `run()`, we'll see it pretty quickly, because a
   bunch of code is going to depend on this function.


```python
import subprocess


def run(path, *cmd):
    return subprocess.run(["git"] + list(cmd), cwd=path)
```

Then we get an horrible backtrace:

```text
self.pid = _posixsubprocess.fork_exec(
        args, executable_list,
        close_fds, sorted(fds_to_keep), cwd, env_list,
        p2cread, p2cwrite, c2pread, c2pwrite,
        errread, errwrite,
        errpipe_read, errpipe_write,
        restore_signals, start_new_session, preexec_fn)
TypeError: expected str, bytes or os.PathLike object, not NoneType
```

That's because the url returned by `create_repo` is None.


```python
class GitServer:
    def __init__(self, tmpdir):
        self.root = tmpdir.join("srv").mkdir()

    def create_repo(self, name):
        dest = self.root.ensure_dir(name)
        gl_push.git.run(dest, "init", "--bare")
        return dest
```

Done!

Just so that the test does have an assertion, we can write:

```python
def test_can_create_a_repo(tmpdir, monkeypatch):
    server = GitServer(tmpdir)
    url = server.create_repo("foo")
    monkeypatch.chdir(tmpdir)
    gl_push.git.run(tmpdir, "clone", url)
    assert tmpdir.join("foo").exists()
```

# The mock

OK, so now we get the tools we need to write the tests for the `main` function.

We'll first write a pytest fixture for our `GitServer`:

```python
# in gl_push/test/conftest.py
import pytest
from gl_push.test.git_server import GitServer

@pytest.fixture
def git_server(tmpdir):
    return GitServer(tmpdir)
```

Thus we can delete the old `test_zero` function in
`tset_gl_push` and use the `GitServer` in our test:

```python
def test_push(git_server, monkeypatch, tmpdir):
    url = git_server.create_repo("foo/bar")
    monkeypatch.chdir(tmpdir)
    foo_dir = tmpdir.ensure_dir("foo")
    gl_push.git.run(foo_dir, "clone", url)
    bar_src = foo_dir.join("bar")
    bar_src.join("README").write("This is the README")
    gl_push.git.run(bar_src, "add", ".")
    gl_push.git.run(bar_src, "commit", "--message", "Initial commit")
    gl_push.git.run(bar_src, "push", "origin", "master:master")
    gl_push.git.run(bar_src, "checkout", "-b", "test1")
    gl_push.git.run(bar_src, "commit", "--message", "test", "--allow-empty")

    with mock.patch("gl_push.gitlab") as mock_gitlab:
        monkeypatch.chdir(bar_src)
        gl_push.main()
        mock_gitlab.ensure_merge_request.assert_called_with(
            "foo/bar",
            "test1",
            title="test1"
        )
```

That's a lot of test code.

The first step is to setup the test by creating a clone of the `foo/bar`
repository, with a branch named `test1`.

We first have to create the `master` branch with an initial commit.
(`GitServer.create_repo()` only created an empty repo), and then
we have to make sure the `test1` branch differs from master by adding an empty
commit on the `test1` branch.

Finally we create a mock of the `gl_push.gitlab` module and assert that
`ensure_merge_request` is called with the correct parameters.

Let's see how the test errors guide us this time:

`ModuleNotFoundError: No module named 'gl_push.gitlab'`

Write `gl_push/gitlab.py`

<hr />

```
AssertionError: Expected call: ensure_merge_request('foo/bar', 'test1', title=None)
Not called
```

And here we are stuck. We need to find the project name, the current branch, so
that we can call `ensure_merge_request()` with the correct arguments.

Doing so requires running `git` commands and this is hard to unit-test.

Let's write some ugly code to get us there:

```python
# in main.py

def main():
    cwd = os.getcwd()
    res = gl_push.git.run(cwd, "remote", "get-url", "origin",
                          capture=True)
    project = "/".join(res.stdout.decode().strip().split("/")[-2:])

    res = gl_push.git.run(cwd, "rev-parse", "--abbrev-ref", "HEAD",
                          capture=True)
    branch = res.stdout.decode().strip()

    title = branch
    gl_push.gitlab.ensure_merge_request(project, branch, title=title)
```

Note how we had to patch `gl_push.git.run` to add a `capture=True` argument:

```python
def run(path, cmd, capture=False):
    stdout = subprocess.PIPE if capture else None
    return subprocess.run(["git"] + list(cmd), cwd=path, check=True,
                          stdout=stdout)

```

Some notes:


* The object returned by `subprocess.run` contains a `stdout` field with is
  a lits of bytes ending with a `\n`. We prefer working with strings without
  the `\n` ending, hence the call to `.decode().strip()`

* To get the project name, we split the URL of the `origin` remote on the
  slashes, then get the last two parts, and re-join them with slash.

It's now time to clean up the mess, by:

* introducing a `run_out` function in `gl_push/git.py`, to factorize the calls to
  `strip()` and `encode()`.

```python

def run_out(path, *cmd):
    res = subprocess.run(["git"] + list(cmd), cwd=path, check=True,
                         stdout=subprocess.PIPE)
    return res.stdout.strip().decode()
```

* extracting the ugly parsing of the URL:

```python
def get_project_name(path):
    url = run_out(path, "remote", "get-url", "orgin")
    return = "/".join(url.split("/")[-2:])
```

* extracting the code that gets the current branch:

```python
def get_current_branch(path):
    return run_out(cwd, "rev-parse", "--abbrev-ref", "HEAD")
```


There! Now the code in `main()` looks much cleaner:

```python
def main():
    cwd = os.getcwd()
    project = gl_push.git.get_project_name(cwd)
    branch = gl_push.git.get_current_branch(cwd)
    title = branch

    gl_push.git.run("push", "origin", "%s:s" % (branch, branch))
    gl_push.gitlab.ensure_merge_request(project, branch, title=title)
```


# Dangers of mocks

OK, so we wrote quite a lot of code and tests, but the main script is completely
broken.

If we try to run `gl-push` we get:

```text
AttributeError: module 'gl_push.gitlab' has no attribute 'ensure_merge_request'
```

That's because we were so focused on the mock that we completely forgot about
the production code.

But how can we write tests for the `gitlab.py` module without hitting the real
GitLab API?

Answer in the next blog post, stay tuned!
