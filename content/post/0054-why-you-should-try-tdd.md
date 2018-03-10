---
slug: why-you-should-try-tdd
date: 2017-09-17T10:11:06.837753+00:00
draft: false
title: Why You Should Try TDD
tags: [testing]
---

TL;DR: You should try using Test Driven Development because it will turn you into a better programmer.

Not convinced? Let me elaborate.

<!--more-->

# Introduction

Throughout this article, I'll be using code taken from a project I'm currently working on: [tsrc](https://github.com/tankerapp/tsrc)

It's a command-line tool to manage several git repositories.

Basically, it reads information from a 'manifest' file to know what repositories to clone or update, like so:

```console
$ mkdir workspace
$ cd workspace
$ tsrc init <manifest-url>
```

The manifest URL is a git url of a repository that contains the manifest file.

Then, when all the repositories have been cloned, you can run:

```console
$ tsrc sync
```

to update all repositories.

More precisely, I'm going to focus on the tests I wrote while adding group support to `tsrc`. That is, when used with
`tsrc init -g foo <manifest-url>`, only the repositories defined in the `foo` group of the manifest will get cloned.

# Improved skills

When doing TDD, there is a cycle of 3 steps:

* Red: write a failing test
* Green: make the test pass
* Refactor: clean up the mess you just made

Because the 3 steps are separate and have different goals, you can use them to practice some specific set of skills.

## Red phase

During the red phase, your only concern is to figure out how to write a failing test.

Usually a test is made of three parts:

* Arrange: initialize resources or objects required by the test
* Act: exercise the production code
* Assert: examine the actual results of the previous action and check they match what was expected

Again, by focusing on each part of the tests, you'll get specific skills.

### Arrange and Act

The first thing we need for adding group support to `tsrc` is a system to define such groups of elements.

But how are we going to write tests without knowing what the production code looks *at all*?

A common technique is to start writing the test "from the middle". You write the code you'd like to have ('act' part), and then work backward and forward to figure out how to do the 'arrange' and 'assert' part.

A simple way to define a group is to call a function with the name of the group and the set of elements. (We're going to use sets because we do not want duplicate elements):

```python
<something>("one", {"foo", "bar"})
<something>("two", {"spam", "eggs"}
```

Then we want to check that each group only contains elements that exist:

```python
<something>.set_elements({"foo", "bar", "spam", "eggs", "other"})
<something>("one", {"foo", "bar"})
<something>("two", {"spam", "eggs"}
```

The 'arrange' part is mostly done, now we are ready to write our assertion:

```python
<something>.set_elements({"foo", "bar", "spam", "eggs", "other"})
<something>("one", {"foo", "bar"})
<something>("two", {"spam", "eggs"}
<something>.get_elements(groups=["one", "two"]) == {"foo", "bar", "spam", "eggs"}
```

Now it's time to write real code, for instance using a `GroupList` class:

```python
group_list = GroupList(elements={"foo", "bar", "spam", "eggs", "other"})
group_list.add("one", {"foo", "bar"})
group_list.add("two", {"spam", "eggs"}
assert group_list.get_elements(groups=["one", "two"]) == {"foo", "bar", "spam", "eggs"}
```

Notice how the *architecture* and *design* of the production code was "driven" by the tests.

Also notice how, even though the production code will probably have to contain a `Group` class,
we do not have to make it part of the public API.

So, by practicing the Act and Arrange part of the tests, you will get better and naming things and designing nice and testable APIs.

### Assert

Focusing on just assertions will help you write better tests too.

At the beginning, you'll be tempted to only use assertions provided by your test framework, but as time goes by you'll learn how to write your own assertions so that the test code gets easier to read.

Let's take an example.

When you run `tsrc init -g foo`, `tsrc` will parse a 'manifest' file, look for the group named 'foo', and for each project of the 'foo' group, will look for its URL and path, and clone it inside the workspace.

Here's what the test could look like:

```python
def test_init(tsrc_cli, git_server, workspace):
    git_server.add_group("foo", ["bar", "baz"])
    git_server.add_repo("other")
    manifest_url = git_server.manifest_url

    tsrc_cli.run("init", manifest_url, "--group", "foo")

    assert workspace.root_path.joinpath("bar").exists()
    assert not workspace.root_path.joinpath("other").exists()
```

I won't explain how the `tsrc_cli`, `git_server` and `workspace` arguments work here [^1], my point is to make you realize the test will be a bit more readable if written like this:


```python

def repo_exists(workspace, repo_path):
    return workspace.root_path.joinpath(repo_path).exists()


def assert_cloned(workspace, repo_path):
    assert repo_exists(workspace, repo_path)


def assert_not_cloned(workspace, repo_path):
    assert not repo_exists(workspace, repo_path)


def test_init(tsrc_cli, git_server, workspace):
    git_server.add_group("foo", ["bar", "baz"])
    git_server.add_repo("other")
    manifest_url = git_server.manifest_url

    tsrc_cli.run("init", manifest_url)

    assert_cloned(workspace, "bar")
    assert_not_cloned(workspace, "other")
```

Some say: *You should write tests that read like a well-written specification*. So, by practicing the "Assert" part of your tests, you will get better at expressing specifications in code, which is a very useful skill.


## Green phase

So the first phase was all about naming things, designing nice APIs and expressing requirements in code.

This phase is all about getting sh\*t done.

Your *only* concern here is to write the least amount of code required for the test to pass.

Thus, practicing this phase will help you at keeping things simple, avoid feature creep, and over-design.

It will also help you following the [YAGNI](https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it) principle.


## Refactor phase

The last phase is all about making the code *clean*. Here your only concern is to change the code without altering the behavior.

There's a lot of techniques to be learned here, like for instance *extracting* classes.

Let's have a look at an example.

Here's how `tsrc` handles the manifest:

* `tsrc init` clones the manifest repository into a hidden `<workspace>/.tsrc/manifest` directory.
* When using `sync`, it:
  * runs `git fetch && git reset --hard origin/master` from the cloned path
  * reads the `manifest.yml` inside the clone path to make sure it is up-to-date.

That means that if the manifest is changed to add or remove a repository, `tsrc sync` will notice it.

The implementation is done in a `Workspace` class:

```python
class Workspace:
    def __init__(self, root_path):
        self.root_path = root_path
        hidden_path = self.root_path.joinpath(".hidden")
        self.manifest_clone_path = hidden_path.joinpath("manifest")
        self.manifest = None

    def init_manifest(self, url,  branch="master", tag=None):
        """ Called by `tsrc init`: clone the manifest in self.manifest_clone_path """
        self._clone_manifest(url, branch, tag)

    def get_repos(self):
        """ Get the list of repos to work with """
        return self.manifest.get_repos()
```


Now we need to add group support.

Notice it is necessary to store information about the groups permanently: after running `tsrc init -g foo`, we need
`tsrc sync` to only update the repositories in the `foo` group.

So we update the Workspace class:

```python

class Workspace:
    def __init__(self, root_path):
        self.root_path = root_path
        hidden_path = self.root_path.joinpath(".hidden")
        self.manifest_clone_path = hidden_path.joinpath("manifest")
        self.manifest_config_path = hidden_path.joinpath("manifest.yml")
        self.manifest = None

    def init_manifest(self, url,  branch="master", tag=None, groups=None):
        self._clone_manifest(url, branch, tag)
        self._save_manifest_config(url, branch, tag, groups)

    def _clone_manifest(self, url, branch, tag):
        ...

    def _save_manifest_config(self, url, branch, tag, groups):
        """ Dump the manifest config to self.manifest_config_path """
        ...

    def _load_manifest_config(self):
        """ Load the manifest config from self.manifest_config_path """
        ...

    def get_repos(self):
        config = self._load_manifest_config()
        groups = config.get("groups")
        return self.manifest.get_repos(groups=groups)
```


And here's a *code smell*. You'll notice that the word "manifest" is all over the place in the Workspace class.

The code is telling us there's a class missing somewhere.

And indeed, look how we can introduce a new 'LocalManifest' class:


```python
class LocalManifest:
    """ Represent a manifest that has been cloned locally inside the
    hidden <workspace>/.tsrc directory, along with its configuration

    """
    def __init__(self, workspace_path):
        hidden_path = workspace_path.joinpath(".tsrc")
        self.clone_path = hidden_path.joinpath("manifest")
        self.cfg_path = hidden_path.joinpath("manifest.yml")
        self.manifest = None

    def init(self, url, branch, tag, groups):
        ...
        self.clone_manifest(url, branch, tag)
        self.save_config(url, branch, tag, groups)

    def save_config(self):
        ...

    def load_config(self):
        ...

    def get_repos(self):
        config = self.load_config()
        groups = config.get("groups")
        return self.manifest.get_repos(groups)


class Workspace:

  def init(self, manifest_url, branch, tag, groups):
      self.local_manifest.init(manifest_url, branch, tag, groups)

  def get_repos(self):
      return self.local_manifest.get_repos()
  ...
```

Practicing this kind of refactoring will be useful in all kind of situations, even when you are not using TDD at all.

# Change the way you work

Doing TDD does not only improve your skill, it also changes the way you work.

## Less fear

By practicing TDD, you'll be writing and running tests *a lot*. So, if you do it well, you'll end up with a nice suite of test you can trust, and you will feel much more confident when refactoring or adding new features.

## Less time spend debugging

Let's see how debugging works depending on the phase you are on:

* red phase: it's very unlikely you are going to introduce bugs *just by writing a new test*. It does happen though. For instance, your new test may be changing the global state in an non obvious way and trigger other test failures. But I'm not sure how you could introduce a bug into the *production code*.
* green phase: since all you care about is making the test pass, usually you'll try to *modify* the production code as less as possible, and instead try to only *add*  new code. If you do this, it's not likely bugs will appear.
* refactor phase: that's when bugs are most likely to appear. After all, you are *changing code that already works*. But, if you have a well-written test suite, depending on which tests fail and how, you should get a pretty good idea about where the bug is.

Bottom-line is: the more you practice TDD and the more you improve your refactoring skills, the less time you will spend debugging.

## Faster context switches

We all know it's hard to get back to work right after a meeting.

If you practice TDD and always make a commit at the end of the refactoring phase, you can know very quickly where you were when you go back to work:

* No git diff: last bug fix of feature is done, you can start working on the new stuff.
* There's a git diff:
  * The tests pass: it's time to refactor
  * The tests fail: it's time to write production code

You can also make a temporary commit like 'Add failing test for feature #3' at the end of the red phase if you like, but I would rather not make it part of the public git history. (Meaning you should squash it with the following commits)

## Getting done faster

Sometimes you'll realize the production code you've just wrote is _already_ feature complete.

Let me show you an example.

The `GroupList` we saw earlier had to be changed to allow groups to include each other.

I had already written tests to make sure that the `get_elements()` method would throw if the group did not exist:

```python
# in test_groups.py
def test_unknown_group():
    group_list = GroupList(elements={"a", "b", "c"})
    with pytest.raises(GroupNotFound):
        group_list.get_elements(groups=["no-such-group"])


# in groups.py
class GroupError:
    pass


class GroupNotFound(GroupError):
    ...


class GroupList:
    ...
    def add(self, name, elements):
        group = Group(name, elements)
        self.groups[name] = group

    def get_elements(groups=None):
        if not groups:
            return self.all_elements
        res = set()
        for group_name in groups:
            if group_name not in self.groups:
                raise GroupNotFound(group_name)
            group = self.groups[group_name]
            for element in groups.elements:
                res.add(element)

```

Then to implement group inclusion, I first wrote a failing test:

```python
def test_includes():
    group_list = GroupList(elements={"a", "b", "c"})
    group_list.add("default", {"a", "b"})
    group_list.add("other", {"c"}, includes={"default"})
    actual = group_list.get_elements(groups={"other"})
    assert actual == {"a", "b", "c"}
```

And then I made the test pass by writing a recursive algorithm, extracting
the parsing of groups inside a `_rec_get_elements` method:

```python
class GroupList:

    ...
    def add(self, name, elements, includes=None):
        group = Group(name, elements, includes=includes)
        self.groups[group.name] = group

    def get_elements(groups=None):
        res = set()
        self._rec_get_elements(res, groups):

    def _rec_get_elements(self, res, groups):
        for group_name in groups:
            if group_name not in self.groups:
                raise GroupNotFound(group_name)
            group = self.groups[group_name]
            for element in groups.elements:
                res.add(element)
            self._rec_get_elements(res, group.includes)
```

After which I was concerned that there may be non-existing groups inside the `includes`, so I wrote a test I thought would fail:

```python
def test_unknown_include():
    group_list = GroupList(elements={"a", "b", "c"})
    group_list.add("invalid", {"a"}, includes={"no-such-group"})
    with pytest.raises(GroupError):
        group_list.get_elements(groups=["invalid"])
```

But nope, the test was already passing because the `GroupNotFound` exception was already thrown by the
recursive method.

Note that I still had to patch the code a tiny bit so that the `GroupNotFound` exception would refer to the "parent group", but the point is the general structure of the code did not have to change much.

Getting 'done' sooner than you expect is a pretty nice feeling to have, trust me :)

# Some advice

## Don't Give Up

The only way to get good at TDD is by practicing. It will take you quite some time before you experience all the nice things I talked about in the previous paragraphs, but I'm convinced they are worth it. So *please* don't give up too soon.

## Beware of caveats

I talked about them on my blog: [When TDD Fails]({{< relref "post/0014-when-tdd-fails.md" >}})

## Avoid classic beginners mistakes

There's a nice article on Uncle Bob's blog: [Giving Up On TDD](http://blog.cleancoder.com/uncle-bob/2016/03/19/GivingUpOnTDD.html)

## Getting started

It can be quite challenging doing TDD inside an existing big code base, especially if there is not a nice test suite already written.

Even if this is the case, it will take you quite some time to get familiar with the test suite, so that you know what to do when certain tests fail.

Here are two easier ways to get started:

* When you are writing a project from scratch (like your next microservice, if you are into this)
* When adding a new dependency.

There's not much to say about starting a new project from scratch, except that the opportunity does not present very often, but I do have things to say about dependencies, so here goes:

## Adding a new dependency

Here's a process you can use when you I try to add a new functionality based on an new dependency, say a new library.

Basically, you write throw-away test code to know how the library works, and only then you write new tests that exercise the production code.

Again, let's use `tsrc` as an example.

I was trying to make sure that in the case the manifest file was incorrect, I would be able to throw nicely detailed errors, for instance:

```yaml
# OK:
groups:
  default:
     repos: [a, b]
  other:
    includes: [default]

# BAD: includes should be a list
groups:
  default:
     repos: [a, b]
  other:
    repos: [c]
    includes: default

# BAD: repos key is missing:
groups:
  default: [a, b]
```

I learned about the `schema` library, so I wrote a test to check if I understood how the library worked:

```python
# in test_schema.py
import schema

def test_invalid_schema():
    foo_cfg = { "foo": {"bar": 42 }
    foo_schema = schema.Schema(
        {"foo": {"bar": str}}
    )
    with pytest.raises(schema.SchemaError) as e:
        foo_schema.validate(foo_cfg)
    assert "42 should be instance of 'str'" in e.value.details
```

Note: this kind of test can also help you check that your build tools are configured properly.

Then I wrote a new test to think about how I would integrate schema parsing into the existing code, here by adding a `schema` argument to my `parse_config_file` function:

```python
# in test_config.py
def test_parse_config_invalid_schema():
    foo_yml = tmp_path.joinpath("foo.yml")
    foo_yml.write_text(textwrap.dedent(
        """
        foo:
            bar: 42
        """
    ))
    foo_schema = schema.Schema(
        {"foo": {"bar": str}}
    )
    with pytest.raises(tsrc.InvalidConfig) as e:
        tsrc.parse_config_file(foo_yml, schema=foo_schema)
    assert "42 should be instance of 'str'" in e.value.details


# in config.py
from schema import SchemaError

def parse_config_file(path, schema=None):
    ...

    cfg = yaml_load(path)

    if schema:
        try:
           schema.validate(cfg)
        except ShemaError as schema_error:
            raise InvalidConfig(path, schema_error)

```

Note how the `test_parse_config_invalid_schema` looks very much like the original `test_invalid_schema`, so after the feature was done, I just had to delete the now useless `test_schema.py` file.

By the way, this process of writing throw-away tests just to help you write better tests afterwards is a technique that you can apply in a lot of situations, adding a new dependency being just an example of this technique.


# Conclusion

And here's all I had to say today. See you some other time!

[^1]: There are pytest fixtures, if you need to know
