---
slug: trying-mypy
date: 2018-04-21T10:17:17.789657+00:00
draft: true
title: "Trying mypy"
tags: [python]
---

This is a story about me being wrong about tests and type systems.

It's also a story of me trying something new and learning a few things.

Let's start at the beginning.

# I don't need types

A few years ago, I was working in a team where the two main languages used were C++ and Python.

Here's what I used to think:

C++ sucks:

* I have to specify types everywhere:
  * I need to know the difference between `int`, `long`, `uin8_t`, `size_t` even if all I want is a goddamn integer.
  * I have to duplicate the signatures of the methods and functions in the header and the source files
* I never know if a compiler warning or error indicates a bug or not
* There's still a lot of bugs the compiler does not catch (race conditions, dangling pointers ....)
* Refactoring is hard: when you change a function signature, you have to fix the code everywhere before you can even run some tests.
* Writing tests in hard: You can't really write isolation tests because mocking and dependency injection in C++ don't really work. Plus, `gtest` sucks.

Python rocks:

* I don't have to think about types if I don't want to. If I *really* need it, I can write an abstract base class, but most of the time duck-typing "just works".
* If I misspell a variable or function name, or if I forgot to import a module, I'll get a test failure immediately.
* For each bug I can quickly add a non-regression test.
* Refactoring is easy: all you have to do is run the tests, look at the failures and fix the code. When the tests pass, you know you're done.
* Writing tests is easy: dependency injection is trivial to do thanks to duck-typing, and you can monkey-patch or mock everything! Plus, `pytest` is awesome!
* Static analysis for Python does not work, pylint is slow, and hard to configure. There are tons of bugs it does not catch, and it is often wrong.
* Types annotations are useless (after all, the interpret does almost nothing with them), except maybe for documentation purposes.

I now think most of these statements are wrong, but it was what I believed at the time.

# Changing my mind

So there I was. Tools and type systems did not matter, all that matter were tests and how easy it was to write them.

All you need to do in order to have tests that you can trust and ship code without bug was to use TDD and write lots and lots of tests.

Here's a list of things that contributed to burst my bubble.


## pyflakes

I started using [pyflakes]() in [vim-ale]. pyflakes is very easy to use, requires no configuration and it's fast.

Suddenly a whole bunch of bugs disappeared: `pyflakes` is very good at finding misspelled variables or missing imports.

So maybe using TDD just to find misspelled variables or missing imports is overkill?

Of course, pyflakes does not catch other errors like calling a function with an incorrect number of arguments but still, it's quite nice to catch these errors *right after the file is saved*, instead of later when a test fails.


## pylint

I've already mentioned how [pylint can be very useful]() if you take the time to configure it properly, so I won't repeat myself here.

But still, it showed that static analysis of Python code did not have to suck after all.

## Gary Bernhardt's talk about ideology

If you haven't seen [ideology by Gary Bernhardt](https://www.destroyallsoftware.com/talks/ideology) I highly recommend it.

Excerpt:

> [This is important] mostly because it will make you better programmers, but also because it will stop you from making angry hacker news comments.

What Gary Bernhardt explains is how and why we end up saying things like *unit tests make type systems unnecessary*, and *type systems make unit tests unnecessary*, which obviously can't be both right at the same time ...

## Javascript and flow

Then there was this time when I had to make a refactoring I a Javascript project.

There were *no tests at all*, and adding them would have been pretty challenging.

But there were [flow]() annotations everywhere. Even if the errors weren't always easy to understand and even sometimes misleading, that helped a lot to build confidence that I was not breaking everything.

So adding type annotations to a language that had a very weak type system maybe was not a waste of time.

## rust

That was the last nail in the coffin. I start re-writing a Python project in rust, and suddenly all this stuff about "if it compiles, it works", and "types system makes unit tests unnecessary* finally started to make sense.

Here's what I learned writing rust:

* Specify types is easy: all you need to annotate are function parameters and return values, and everything else is inferred by the compiler.
* Error messages and warning almost always indicate a bug or an inefficient way of doing things.
* Types can actually help you!

Let me give you a few examples:

* Anything that can fail returns a *type* (like `Option` or `Result`) that forces you to handle errors. Compare this to using exceptions or return values in other languages...
* You can't copy something unless implements the `Copy` trait.
* The `Send` and `Sync` traits define how you can use a type across threads.
* and more!

In the mean time, using TDD with rust is enjoyable. I even wrote a test to make sure a certain bug would be caught *at compile time*.

That's when I completely changed my mind: Type system did not have to suck, they could be very useful, and you could combined them with tests and get the best of two worlds.

So, here's how a "I don't need no stinking' types" kind of guy decided to give mypy a try.

# Trying mypy


## How mypy works


Here's a contrived example:

```python
def is_odd(num):
    return num % 2 == 0


if is_odd("this sentence contains %s"):
    print("ok")
```

We use `is_odd`, which  is obviously a method that only works with number, with a string.

But since the string contains `%s`, Python will happily assume we are trying to format it, and the bug will go un-noticed.
`is_odd` will simply return False, because we are *also* allowed to compare strings and numbers in Python.

Without type annotations, mypy detects nothing:
```
$ mypy foo.py
<nothing>
```

But if we add type annotations and re-run mypy, we do get an error message:

```python
def is_odd(num: int) -> bool:
    return num % 2 == 0


if is_odd("this sentence contains %s"):
    print("ok")
```

```
$ mypy foo.py
foo.py:5: error: Argument 1 to "is_odd" has incompatible type "str"; expected "int"
```

Thus, you can use mypy in a loop:

* Start by annotating a few functions.
* Run mypy on your source code.
* If it detects some errors, either fix the annotations on the code.
* Back to step one

This is called "gradual typing".

## Designing an experiment

The goal of the experiment is to check if going through the trouble of adding type annotations is worth it.

To test this hypothesis, I first needed an existing project. I used tsrc.

* It's not too big, so the experiment will not take too long.
* It's not too small, so we'll have enough experimental data.

I also used a project where lots of tools were already used in the hope of catching bugs:

* Every pull request was reviewed by other humans
* Two static analyzers (pylint and pyflake) were ran for  each pull request
* McCab complexity was measured for each and every function and method of the code base and was not allowed to go above 10.
* TDD was used throughout the development of the projects

Then I had to define what I meant by "worth it".

There are many things said about types annotations like:

* It make it easier for external contributors to understand the code
* It helps during refactorings
* It facilitates maintenance of large projects

Those may be true, but they are hard to measure.

So I ask myself something something else:

* One: even with everything else (linters, tests, reviews ...), were there bugs that only type annotations would catch?
* Two: were the changes required to have mypy run without errors improving the quality of the code?

I know the second question is a bit subjective. I'm still going to use this metric because it's one that really matters to me.

The protocol will thus be:

* Use the gradual typing loop until every function and method is annotated
* Make a note of every non-trivial patch. (That is anything that is *not* just adding annotations)
* When the loop is finished, take a look at each of the patch, and ask if a bug was found, and whether it improved the quality of the code.

Before I continue, I should tell you I used mypy with two important options:

* `--ignore-missing-imports`: tsrc depends on libraries for which no type stub exist.
* `--strict-optional`: If you have a string that can None, you must use `Optional[str]` instead of just `str`. I chose that because:
  * Errors relative to None are quite frequent
  * `--strict-optional` is going to be the default in a future mypy release.

## Looking at patches

Let's look at trivial patches first:

### Truthy string


```python
def find_workspace_path() -> Path:
    head = os.getcwd()
     tail = True
     while tail:
         tsrc_path = os.path.join(head, ".tsrc")
         if os.path.isdir(tsrc_path):
             return Path(head)
        else:
            head, tail = os.path.split(head)
    raise tsrc.Error("Could not find current workspace")
```

This function starts by checking there is a `.tsrc` hidden directory in the working path.
If not, it goes through every parent directory and check if the `.tsrc` directory is here. If it reaches the root of the  filesystem (the second value of `os.path.split` is None), it raises an exception.

mypy did not like that `tail` started as a boolean, and then was assigned to a string.

We can fix that by using a non-empty string, with a name that reveals the intention:

```patch
- tail = True
+ tail = "a truthy string"
     while tail:
```

An other way would be to use a type like `Union[bool,str]` but that would be more confusing I think.

Anyway, I'm not sure the quality of the code improved there. No point for mypy.




### save_config


```python
class Options:
    def __init__(self, url, shallow=False) -> None:
        self.shallow: bool = shallow
        self.url: str = url


def save_config(options: Options):
    config = dict()
    config["url"] = options.url
    config["shallow"] = options.shallow

    with self.cfg_path.open("w") as fp:
        ruamel.yaml.dump(config, fp)
```

We are using `save_config` to serialize a "value object" (the `Options` class) into a yaml file.

mypy saw the first two lines, `config = dict()`, `config["url"] = options.ul` and wrongly deduced that `config` was a dict from strings to strings.

Then it complained about `config["shallow"]` that was assigned to a boolean.

We can fix that by forcing the `config` type:

```patch
- config = dict()
+ config: Dict[str, Any] = dict()
```

This a bit annoying, but the type annotation makes it clearer what the `config` is. 1 point for mypy.

## encoding project names


When you use the GitLab API, you often have to use the 'project id'. The doc says you can use the `<namespace>/<project_name>` string if it is "url encoded", like this:

```
Get info about the Foo project in the FooFighters namespace:
GET  /api/v4/projects/FooFighters%2Foo
```

In python, the naive approach does not work:

```python
import urllib.parse

>>> urllib.parse.quote("FooFighters/Foo")
FooFighters/Foo
```

Instead you have to specify a list of "safe" characters, that is characters that you *don't* need to encode.

The doc says the default value is "/".

Thus, here's what we use in `tsrc.gitlab`:

```python
project_id = "%s/%s" % (namespace, project)
encoded_project_id = urllib.parse.quote(project_name, safe=list())
```

mypy saw that the default value was a string, so he complained we were using a list instead. We fixed it by:

```patch
-        encoded_project_name = urllib.parse.quote(project_name, safe=list())
+        encoded_project_name = urllib.parse.quote(project_name, safe="")
```

Here, mypy forced us to follow an implicit convention. There are two ways to represent a list of characters in Python. A real list: `['a', 'b', 'c']`, or a string: "abc". The authors of the `urllib.quote()` function decided to use the second form, so it's a good thing we follow this convention too.

An other win for mypi.

### Bugs found

Yes, mypy found bugs that tests, all the linters and all the reviewers did not find.

Here are a few of them. Feel free to try and find the bug yourself, the answer will be given after the ⁂ symbol.

#### handle_stream_errors

```python
class GitLabAPIError(GitLabError):
    def __init__(self, url: str, status_code: int, message: str) -> None:
        ...

def handle_stream_errors(response: requests.models.Response) -> None:
     if response.status_code >= 400:
     raise GitLabAPIError(
        response.url, "Incorrect status code:", response.status_code)
```


This code wraps calls to the GitLab API, and arrange for a particular GitLabAPIError to be raised, when we make a "stream" request. (For instance, to download a GitLab CI artifact):


<center>⁂</center>

The problem here is that we inverted the `status_code` and `message` parameter. Easy to fix:


```patch
-        raise GitLabAPIError(
-           response.url, "Incorrect status code:", response.status_code)
+        raise GitLabAPIError(
+           response.url, response.status_code, "")
+
```

The bug was not caught because the code in question was actually copy/pasted from a CI script (and you usually don't write tests for CI scripts).

We actually don't need to streamed response anywhere in tsrc, so this is in fact dead code.


#### handle_json_errors


```python
def handle_json_errors(response: requests.models.Response):

    try:
         json_details = response.json()
     except ValueError:
     json_details["error"] = (
         "Expecting json result, got %s" % response.text
     )

    ...

    url = response.url
    if 400 <= status_code < 500:
        for key in ["error", "message"]:
            if key in json_details:
                raise GitLabAPIError(url, status_code, json_details[key])
         raise GitLabAPIError(url, status_code, json_details)
    if status_code >= 500:
        raise GitLabAPIError(url, status_code, response.text)
```

This one is slightly more interesting. It is located near the previous one and handles errors for the calls to the GitLab API which returns json objects.

We of course have to catch 500 errors, which hopefully happen not often.

In case of a status code between 400 and 499, we know there was a problem in the request we made, but we need to tell the user why the request was rejected.

Most of the time the GitLab API returns a json object containing a `error` or `message` key, but sometimes neither keys is found in the returned json object, and sometimes no valid json object is returned at all.

So we have to check for both keys in the json object, and if not found (if we exit the for loop), just store the entire JSON response in the exception.

<center>⁂</center>

The bug is in the second `raise GitLabAPIError`. We are passing an entire object where the `GitLabAPIError` expected a string.

The fix was:

```patch
- raise GitLabAPIError(url, status_code, json_details)
+ raise GitLabAPIError(url, status_code, json.dumps(json_details, indent=2))
```

Again, this was hard to catch with tests. The case where the json returned by GitLab did *not* contain a `error` or `message` key only happened once in the lifetime of the project (which explain why the code was written), so manual QA and unit tests did not need to check this code path.

Anyway, note we did not blindly wrote something like `str(json_details)` to convert the json object to a string. We found out it was used in a message displayed to the end user, thus we use `json.dumps(json_details), indent=2)` to make sure the message contains neatly indented json and is easy to read.


#### LocalManifest

```python
class LocalManifest:
    def __init__(self, workspace_path: Path) -> None:
        hidden_path = workspace_path.joinpath(".tsrc")
        self.clone_path = hidden_path.joinpath("manifest")
        self.cfg_path = hidden_path.joinpath("manifest.yml")
        self.manifest: Optional[tsrc.manifest.Manifest] = None

    def update(self) -> None:
        ui.info_2("Updating manifest")
        tsrc.git.run_git(self.clone_path, "fetch")
        tsrc.git.run_git(self.clone_path, "reset", "--hard", branch)

    def load(self) -> None:
        yml_path = self.clone_path.joinpath("manifest.yml")
        if not yml_path.exists():
            message = "No manifest found in {}. Did you run `tsrc init` ?"
            raise tsrc.Error(message.format(yml_path))
        self.manifest = tsrc.manifest.load(yml_path)

    @property
    def copyfiles(self) -> List[Tuple[str, str]]:
        return self.manifest.copyfiles

    def get_repos(self) -> List[tsrc.Repo]:
        assert self.manifest, "manifest is empty. Did you call load()?"
        return self.manifest.get_repos(groups=self.active_groups)
```

After you run `tsrc init git@example.com/manifest.git`, the manifest is cloned inside `<workspace>/.tsrc/manifest`.

Thus, the contents of the `manifest.yml` is in `<workspace>/.tsrc/manifest/manifest.yml>`.

The `LocalManifest` class represent this manifest repository.

Here's what happen, when you run `tsrc sync`:

* `local_manifest.update()`: The repository in `<workspace>/.tsrc/manifest>` is updated by running `git fetch; git reset --hard origin/master`
* `local_manifest.load()`: The `manifest.yml` file is parsed, and its contents are stored in the `self.manifest` attribute.
* The `Syncer` class calls `local_manifest.get_repos()` to find out the list of repositories to clone or synchronise.
* The `FileCopier` uses `local_manifest.copyfiles` to perform file copies.

<center>⁂</center>

It's not really a bug, but mypy forced us to acknowledge that `LocalManifest.manifest` starts as None, and only gets its real value after `.load()` has been called.

We already have an `assert` in place in `get_repos()`, but mypy forced us to add a similar check in the `copyfiles` getter:

```patch
    @property
    def copyfiles(self) -> List[Tuple[str, str]]:
    +    assert self.manifest, "manifest is empty. Did you call load()?"
        return self.manifest.copyfiles
```

#### GitServer

Some of the tests for tsrc are what we call end-to-end tests:

Here's how they work:

* We create a band new temporary directory for each test
* In it, we create a `srv` directory with bare git repositories
* Then, we create a `work` directory and we run tsrc commands from there.

Thus, we don't have to mock file systems or git commands (which is doable but pretty hard), and things are easy to debug because in case of problem we can just `cd` to the test directory and inspect the state of the git repositories by hand.

Any way, those tests are written with a test helper called `GitServer`.

You can use this class to create git repositories, push files on some branches, and so on:

Here's what the helper looks like:


```python
    def add_repo(self, name: str, default_branch="master") -> str:
        ...
        url = self.get_url(name)
        return url

    def push_file(self, name: str, file_path: str, *,
                  contents="", message="") -> None:
        ...
        full_path = ...
        full_path.parent.makedirs_p()
        full_path.touch()
        if contents:
            full_path.write_text(contents)
        commit_message = message or ("Create/Update %s" % file_path)
        run_git("add", file_path)
        run_git("commit", "--message", commit_message)
        run_git("push", "origin", "--set-upstream", branch)

    def tag(self, name: str, tag_name: str) -> None:
        run_git("tag", tag_name)
        run_git("push", "origin", tag_name)

    def get_tags(self, name: str) -> List[str]:
         src_path = self.get_path(name)
         rc, out = tsrc.git.run_git_captured(src_path, "tag", "--list")
         return out
```

You can use it like this:

```python
def test_tsrc_sync(tsrc_cli, git_server):
    git_server.add_repo("foo/bar")
    git_server.add_repo("spam/eggs")
    manifest_url = git_server.manifest_url
    tsrc_cli.run("init", manifest_url)
    git_server.push_file("foo/bar", "bar.txt", contents="this is bar")

    tsrc_cli.run("sync")

    bar_txt_path = workspace_path.joinpath("foo", "bar", "bar.txt")
    assert bar_txt_path.text() == "this is bar"
```

<center>⁂</center>

The bug is in `get_tags`:

```patch
    def get_tags(self):
         rc, out = tsrc.git.run_git(src_path, "tag", raises=False)
-        return out
+        return out.splitlines()
```

The `get_tags` methods is also dead code. It has an interesting story.

The need for the `GitServer` helper occurred when I started writing end-to-end tests for tsrc and discovered I needed a test framework to write those end-to-end test.

It was vital that the `GitServer` implementation uses clean code.

* One, we must be sure `GitServer` has no bugs. Otherwise, we may get stuck looking for bugs in our production code when tests fail.
* For the same reason, `GitServer` should be easy to change. There will almost certainly be features added in tsrc that will require adapting `GitServer` code in order to properly test it.

So to have a clean implementation of the `GitServer` I of course used the best technique I know of: TDD.

![yo dawg tests](/pics/yo-dawg-test.jpg)

You can find some of them in the [test_fixtures.py]() file.

Anyway, I was writing an end-to-end test for tsrc that involved tags.

I thought: "OK, I need a `.tag()` method in `GitServer`. So I also need a `get_tags()` method to check the tag was actually pushed".   Thus I wrote the `get_tags` method, forgetting to write a failing test for `GitServer` first (that still happens after 5 years of TDD, so don't worry if it happens to you too.). At that point I only had my end-to-end test failing, so I made it pass and completely forgot about the `get_tags()` method.


#### Executors and Tasks

In the implementation of tsrc we often have to loop over a list of items, perform actions an each of them and record which one failed, and when the loop is done, display the error messages to the user.

For instance:

```
tsrc sync
* (1/2) foo/bar
remote: Counting objects: 3, done.
...
Updating 62a5d28..39eb3bd
error: The following untracked working tree files would be overwritten by merge:
	bar.txt
Please move or remove them before you merge.
Aborting
* (2/2) spam/eggs
Already up to date.
Error: Synchronize workspace failed
* foo/bar: updating branch failed
```

Or:

```
$tsrc foreach
:: Running `ls foo` on every repo
* (1/2) foo
$ ls foo
bar.txt
* (2/2) spam
$ ls foo
ls: cannot access 'foo': No such file or directory
Error: Running `ls foo` on every repo failed
* spam
```

So in order to keep things DRY [^1], we have some high-level code that only deals with loop and error handling:

```python

class Task(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def description(self) -> str:
        pass

    @abc.abstractmethod
    def display_item(self, _) -> str:
        pass

    @abc.abstractmethod
    def process(self, _) -> None:
        pass


class SequentialExecutor():
    def __init__(self, task: Task) -> None:
        self.task = task
        self.errors: List[Tuple[Any, tsrc.Error]] = list()

    def process(self, items: List[Any]) -> None:
        if not items:
            return True
        ui.info_1(self.task.description())

        self.errors = list()
        for item in enumerate(items):
            ...
            self.process_one(item)

        if self.errors:
            self.handle_errors()

    def process_one(self, item) -> None:
        try:
            self.task.process(item)
        except tsrc.Error as error:
            self.errors.append((item, error))

    def handle_errors(self) -> None:
        # Display nice error message
        ...
        raise ExecutorFailed()
```

Thus we can inherit from `Task` to implement `tsrc sync`:

```python
class Syncer(tsrc.executor.Task):

    def process(self, repo: tsrc.Repo) -> None:
        ui.info(repo.src)
        self.fetch(repo)
        self.check_branch(repo)
        self.sync_repo_to_branch(repo)

    def check_branch(self, repo):
        current_branch = tsrc.git.get_current_branch(repo_path)
        if not current_branch:
            raise tsrc.Error("Not on any branch")
```

Ditto for `tsrc foreach`:

```python
class CmdRunner(tsrc.executor.Task):

    def process(self, repo: tsrc.Repo) -> None:
        full_path = self.workspace.joinpath(repo.src)
        rc = subprocess.call(cmd, ...)
        if rc != 0:
            raise CommandFailed
```

<center>⁂</center>


The bug is in here:

```python
+    def process(self, items: List[Any]) -> None:
         if not items:
             return True
```

This is the result of a bad refactoring. `Executor` used to track success of task by looking at the return value the `process()` method.

After a while, I found out it was clearer to just use exceptions for that, mostly when I implemented the `Syncer` class. (You can just raise an exception instead of adding lots of `ifs`).

But the early `return True` was left. Here `mypy` found something that would have puzzled an external reader. Almost everything function or method dealing with Executors and Tasks in tsrc either return None or raise Exception. What is that boolean doing here?

There were of course no tests left that checked the return value of `process` (they got refactored at the same time of the rest of the code), so the bug went unnoticed.


## run_git

The last changed required by mypy was also pretty interesting. Here's the deal.

In tsrc, we often need to run `git` commands, but we can run them in two very different ways:

* We can either just run the command and let its output directly being displayed to the user. This is useful for things like `git fetch` which can take some times and for which the output contains an indication of progress for the user.
* Or we just need to run the command, capture its output and deal with it as a value. For instance, if we want to get the url of the "origin" remote, we can call `git remote get-url origin`.
* In both cases, we must handle the possibility that the command can fail.

Here's what the implementation looked like:

```python
def run_git(working_path, *cmd, raises=True):
    """ Run git `cmd` in given `working_path`

    If `raises` is True and git return code is non zero, raise
    an exception. Otherwise, return a tuple (returncode, out)

    """
    git_cmd = list(cmd)
    git_cmd.insert(0, "git")
    options = dict()
    if not raises:
        options["stdout"] = subprocess.PIPE
        options["stderr"] = subprocess.STDOUT

    process = subprocess.Popen(git_cmd, cwd=working_path, **options)

    if raises:
        process.wait()
    else:
        out, _ = process.communicate()
        out = out.decode("utf-8")

    returncode = process.returncode
    if raises:
        if returncode != 0:
            raise GitCommandError(working_path, cmd)
    else:
        return returncode, out
```

And here's how to use it:

```python
# run `git fetch`, leaving the output as-is
run_git(foo_path, "fetch")

# run git remote get-url origin
rc, out = run_git(foo_path, "remote", "get-url", "origin", raises=False):
if rc == 0:
    # Handle the case where there is no remote called 'origin'
    ...
else:
    # Do something with out
```

Here's an other place we used `run_git`: we have a command named `tsrc status`, which displays a summary of the whole workspace. Here what's its output looks like:

```
tsrc status
* foo master ↓1 commit
* bar devel ↑1 commit
```

And here is the implementation:

```python
class GitStatus:

    def update_remote_status(self):
        _, ahead_rev = run_git(
            self.working_path,
            "rev-list", "@{upstream}..HEAD",
            raises=False
        )
        self.ahead = len(ahead_rev.splitlines())

        _, behind_rev = run_git(
            self.working_path,
            "rev-list", "HEAD..@{upstream}",
            raises=False
        )
        self.behind = len(behind_rev.splitlines())
```


Found the bug yet?

<center>⁂</center>

The code in `update_remote_status()` assumes that `git rev-list` outputs a list of commits, and then count the lines in the output.

This works well if there *is* a remote branch configured:

```
$ git revlist HEAD..@{upstream}
30f729a6a0ec3926cf063f5f8a3953b89d7b252e
ef564f0ef38a163beb3db52474ac4e256a6c2cd4
```

But if not remote is configured, the git command will fail with a message looking like:
```
$ git revlist HEAD..@{upstream}
fatal: no upstream configured for branch 'dm/foo'
```

Since `update_remote_status()` does not check the return code, `self.ahead_rev` and `self.behind_rev` both get set to `1`, and the output looks like:

```
* foo other-branch ↑1↓1 commit
```

Oops.

<center>⁂</center>

But there is more to it than just this bug.

An interesting thing happened when I tried to annotate the `run_git` function.

I first had to use a `Union` type because the type of the return value depends on the `raises` parameter.

```python
def run_git(working_path: Path, *cmd: str, raises=True) ->
      Union[Tuple[int, str], None]:
    pass
```

But then mypy complained for each and every line that used `run_git` with `raises=False`:

```
rc, out = run_git(..., raises=False)

foo.py:39: error: 'builtins.None' object is not iterable
```

I thought about this and found out it was cleaner to split `run_git` into `run_git` and `run_git_captured`:

```python
def run_git(working_path: Path, *cmd: str) -> None:
    """ Run git `cmd` in given `working_path`

    Raise GitCommandError if return code is non-zero.
    """
    git_cmd = list(cmd)
    git_cmd.insert(0, "git")

    returncode = subprocess.call(git_cmd, cwd=working_path)
    if returncode != 0:
        raise GitCommandError(working_path, cmd)


def run_git_captured(working_path: Path, *cmd: str, check=True) -> Tuple[int, str]:
    """ Run git `cmd` in given `working_path`, capturing the output

    Return a tuple (returncode, output).

    Raise GitCommandError if return code is non-zero and check is True
    """
    git_cmd = list(cmd)
    git_cmd.insert(0, "git")
    options: Dict[str, Any] = dict()
    options["stdout"] = subprocess.PIPE
    options["stderr"] = subprocess.STDOUT

    returncode = process.returncode
    if check and returncode != 0:
        raise GitCommandError(working_path, cmd, output=out)
    return returncode, out
```

True, there's a bit more code and slightly duplication but:

* The multiple `if raises` in the original implementation are gone. Less `if` in a function is always a win.
* The `raises` parameter did too very different things:
   * One, it changed the return type of the function
   * Two, it forced the caller to explicitly handle the case where the command fails.

Now the intent about whether you want to capture the output or not is encoded *in the name of the function* (`run_git_captured` instead of `run_git`).

Also note that you can't forget about checking the return code anymore.

You can either write:

```python
_, out = run_git_captured(repo_path, "some-cmd")
# We know `out` is *not* an error message, because if `some-cmd` failed, an exception would have been raised
# before `out` was set.
```


Or you can be explicit about your error handling:

```python
rc, out = run_git_captured(repo_path, "some-cmd", check=False)
if rc == 0:
    # Ditto, out can't be an error message
else:
    # Need to handle error here
```

That alone would be a good reason to use mypy I think :)


# Using mypy in production


You may we wondering why the `dm/mypy` branch was not merged, then.

Well, the reason is that I really don't like the syntax you have to use in Python versions less that 3.6 to annotate *variables*:

```python
# OK in python3.5

def foo(bar: int) -> bool:
    pass

foo: Any = 42
# Not OK for Pyton 3.5, use:
foo = 42  # type: Any
```

So, I prefer to wait until tsrc does not need to support Python3.5 any more.

There is also a mode of mypy I did not use, which produces an error if *any* annotation is missing. For instance, I did not add annotation for every member of every class.

I'm still curious about the other benefits of type annotations I could not check (maintainability, code comprehension, ease of refactorings ...), but that will have to be with an other project.

I could also have tried writing code using *only* type annotations to find mistakes (no tests, no linters ...), but I'm so used to TDD and linters I'm sure I won't enjoy the experience.

Feel free to try and tell me about it, though!

# Conclusion

We saw how mypy, while stilling making relative few false positives, still found inconsistencies, a few bugs, and even design problems.


You see, we are terrible at spotting mistakes in our own code.

That's why we try and multiply the techniques hoping each of them will find different types of mistakes.

* We ask other humans to look at our code (during code reviews or peer programming)
* We use static analyzers to find mistakes in the code automatically
* We use tests to try and prove ourselves the code works as it should
* We use TDD to look at the code both from the 'production' perspective (when we go from red to green), and from a 'quality' perspetive (when we go from green to refactor).


Type annotations, even in a dynamic language like Python, and providing you have a good type checker, are just an other technique we can use.

Think about it for your next project!

[^1]: DRY stands for "Don't Repeat Yourself"
