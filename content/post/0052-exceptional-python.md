---
authors: [dmerej]
slug: exceptional-python
date: 2017-08-20T08:09:38.013514+00:00
draft: false
title: Exceptional Python
tags: ["python"]
summary: |
  Stuff I learned while trying to implement proper error management
  in Python code.
---

# Introduction: Error management

Sometimes, things go wrong. We have plenty of ways of expressing this in the English language:

 * Something unexpected occurred
 * Something went south
 * SNAFU (Situation Normal, All F\*cked Up)
 * Shit hit the fan
 * [The god-damned plane crashed into the mountain!](https://www.youtube.com/watch?v=P7lGGhHZSZs)
 * ...

When writing software, we tend to use error codes or exceptions.

# Why should I care?

You should care because errors and unexpected things _will_ happen.

When they do, you will need all the information you can to be able to understand what happened and fix potential bugs.

The same applies to users of your APIs. If you do not handle errors well, every time the API is misused, and users cannot understand what's wrong, they'll get frustrated very quickly. If you are lucky, they may go and try to find answers in the documentation but many of them will just quit.

Lastly, your end users need to know what yo do when error occurs. They want to know what happened *and*, more importantly, what they should do to fix it.

So, proper error handling is key. You sure don't want your product to be
featured in the [Daily WTF error'd series](https://thedailywtf.com/series/errord), do you?


# Part One: Various Error Handling Techniques

{{<note>}}
This section is mostly theoretical. If you want more concrete stuff, feel free to skip directly to [part 2](#part-two-a-concrete-example)
{{</note >}}



# In Bash

When you are using bash, you usually run several extern commands, for instance:

```bash
cd project
git pull
pylint project
pytest
```

Each of these commands has a return code that you can access with a special variable called `$?`.

The return code is 0 when the command succeeds, and can take many other values when something goes wrong. As Tolstoy said:

> Happy families are all alike; every unhappy family is unhappy in its own way.


For instance, `pytest` as 6 different possible return codes:

* 0 when all the tests passed
* 1 when tests were collected and run but some of the tests failed
* 2 when test execution was interrupted by the user
* and more [^1]

There are two problems with this approach:

* You have to check the return code all the time, otherwise the code will continue executing, ignoring previous errors. (You can fix this by calling `set -e` at the top of the script, though)
* When something fails, the only information you have is a number. (And maybe the output, depending on how the script is written)


## In C

When you write in C, you are supposed to check the returned value of every function you call.

Sometimes, it's an integer. For instance:

```C
int size = ...;
FILE* fp = ...;
char buff[size];
int n = fread(buff, size, 1, fp);
if (n < size) {
  // Handle "short read"
}
```

Other times, you are getting a null pointer, and you have to check a special variable called `errno`:

```C
FILE* fp = fopen("foo.cfg", "r");
if (!fp) {
  if (errno == ENOENT) {
    fprintf(stderr, "Could not find foo.cfg\n");
  }
}
```

Here, you don't even have an error message anywhere, all you get in a number. (ENOENT is just a `#define ENOENT 2`)

{{< note >}}
There's a tool called `errno` in [moreutils](https://joeyh.name/code/moreutils/) that can help you if for some reason all you want to convert the value of errno to a human-readable message.
{{</ note >}}

All of this means you have to carefully check the return code of all the functions you called.

If you're using `gcc`, you can trigger a warning when the caller does not check the returned value like so:

```C
/* in foo.h */
int foo() __attribute__((warn_unused_result));

/* in foo.c */
{
  foo();  // triggers a warning
}
```

but then people can ignore the warning &hellip;

# In Go

In Go, functions can return several values.

Functions that may fail are supposed to return a `Error` object along the result, like so:


```go
file, err := os.Open("foo.cfg")
if err != nil {
  ...
}
// Do something with file
```

Contrary to C it's harder to ignore the return value.

You can use something like:
```go
file, _ := os.Open("foo.cfg");
```

but there are linters which will forbid you to do that.

Unlike C, you can add all sorts of metadata to your error.

All you need is to declare a custom struct and implement an `Error` method:

```go
type InvalidConfigError struct {
    Path string;
    Details string
}

func (e *InvalidConfig) Error() string {
	return fmt.Sprintf("%s: %s", e.Path, e.Details)
}

func readConf() (Config, error) {
  // ...
  file, errOpen := os.Open("foo.cfg");
  if errOpen := nill {
    return nil, &InvalidConfigError{"foo", "could not open file"};
  }

  parsed, errParse := parseYaml(file);
  if errParse != nill {
    return nil, &InvalidConfigError{"foo", "invalid YAML syntax"};
  }

  return parsed, nil;
}
```

Using it is a bit painful though, because you have to try and convert it:


```go
func main() {
    config, err := readConf();
    if err != nil {
        invalidConfig, ok := err.(*InvalidConfig)
        // ok will be false if conversion fails
        if ok {
            fmt.Printf("%s:%s", invalidConfig.Path, invalidConfig.Details);
        }
    }
    // Do someting with config ...
}
```

# In Java

In Java you use exceptions instead, with the `throw` and `catch` keywords.

Like Go, you can create your own type of exceptions.

But there are two key differences:

* In a `catch` block you can specify what kind of errors you wish to handle. For instance `catch (FooException)` will catch all exceptions that are an instance of the `FooException` class (maybe via inheritance)
* They also came with a *backtrace*, which lists all the functions that were called when the exception occurred.


There's a catch, though. Let's look at this example:

```java
public class Foo {

    public static void readConf() {
        FileInputStream fs = new FileInputStream("foo.cfg");
    }

    public static void main() {
      readConf();
      ....
    }
}
```

If you try to compile that, you'll get an error:

```text
Foo.java:5: error: unreported exception FileNotFoundException;
must be caught or declared to be thrown
  FileInputStream fs = new FileInputStream("foo.cfg");
```

Java is telling you that you can choose to either:

* Deal with the error right now
* Or let the caller do it.

If no-one catches the exception in the chain of callers, the exception is called "uncaught" and the whole program terminates after printing the backtrace.

Because Java is Java, you have to be explicit about it, like so:

```java
public void readConf() throws FileNotFoundException {
    FileInputStream fs = new FileInputStream("foo.cfg");
}

public static void main(String[] args) throws FileNotFoundException {
    readConf();
    System.out.println("hello");
}
```

This is a bit painful, so there are Java programmers who prefer only using "unchecked" errors so that they don't have to declare explicitly what each method can throw.

```java
/* This error is unchecked because it inherits RuntimeException */
class FooException extends RuntimeException {
  private string path;
  private string details;
    // ...
}

public static void readConf() {
    try {
        FileInputStream fs = new FileInputStream("foo.cfg");
    }
    catch (FileNotFoundException e) {
        throw new FooException("foo.cfg", "file not found");
    }
}

// Look Ma, no 'throws' declaration!
public static void main(String[] args) {
}
```

Note how we have to wrap the `FileNotFoundException` and re-throw our own error.

# In other languages

I could have talked about functional languages, where you use a sophisticated type system:

```elm
type alias Person = { name : String , age : Maybe Int }

canBuyAlcohol user =
  case user.age of
    Nothing -> false
    Just age -> (age >= 21)
```

or about Javascript, where you can handle errors in callbacks:

```javascript
const prom = new Promise((resolve, reject) => {
  if (ok) {
    resolve('value');
  } else {
    reject('error');
  }
});
```

but there's so different than Python that I don't have much to say about them.


# In Python

With Python, you usually use `try` and `except`.

But the nice thing is that you you have a lot of flexibility:

* You can use `errno` like in C:

```python
try:
    open("foo.cfg")
except OSError as e:
    if e.errno == errno.ENOENT:
        sys.stderr.write("File not found")
```

although in Python3 you would rather do:

```python
try:
   open("foo.cfg")
except FileNotFoundError:
   print("File not found", file=sys.stderr)
```

* You can use tuples as return values like in Go:

```python
def run_cmd(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    rc = result.returncode
    out = result.stdout

    return (rc == 0, out.decode().strip())


ok, out = run_cmd(["git", "rev-parse", "--abbrev-ref", "@{u}"])
if ok:
    print("You are tracking", out)
else:
    print("You are not tracking any branch")
```

You can also pass callbacks to deal with errors:

```python
def try_something(on_error=None);
    try:
      ...
    except Error as e:
        on_error(e)

def log_error(e):
    log.error(e)

try_something(on_error=log_error)
```

## Custom exceptions

In Python2, exceptions used to always have a string attribute named `.message`.

That's because it was possible to raise errors for which the constructor only took one argument, using a special syntax like this:

```python
# Only works in Python2!

def foo():
    raise Exception, "Oh noes!"
    # calls Exception("Oh noes")

try:
    foo()
cacth Exception, e:
    print(e)
```

In Python3, the special syntax is gone, and all exceptions now have a `args` attribute, which is just a tuple of any type.

This means that when you create you own type of exception, you will need to call `super().__init__()` so that the `args` attribute is properly set, like so:

```python
class InvalidConfigError(RuntimeError)
    def __init__(self, path, details):
        self.path = path
        self.details = details
        super().__init__(path, details)

    def __str__(self):
        return f"{self.path}: {self.details}"


def read_config(path):
    try:
      ...
    except FileNotFoundError:
        raise InvalidConfigError(path, "not found")

    try:
      ...
    except YAMLError:
        raise InvalidConfigError(path, "invalid YAML syntax")

def main():
    try:
        read_config()
    except InvalidConfigError as e:
        sys.exit(e)
```


## Assert and exit

Note that there are other ways for a Python program to terminate other that an uncaught exception.

For instance, you can use `sys.exit(42)` to force an exit with the given error code.

Because it's common to display a message to `stderr` when you exit with a non-zero code, you can use `sys.exit("<a message here>")` to display an error message and immediately exit afterwards.

You can also use assertions, like so:

```python
def foo(self):
    assert self.bar, "Calling foo() when self.bar is empty"
```

However `sys.exit()`  and `assert` are using exceptions under the hood, namely `SystemExit` and `AssertionError`. (The only difference being that `sys.exit()` does not print a backtrace).

So you can catch both assertions failures and `sys.exit` calls as usual:

```python
try:
   some_script()
except SystemExit as e:
   print("script failed with", e.code)
```

So, given all this flexibility, what's the best way to handle errors in Python?

# Part Two: A Concrete Example

## Introduction

I'm going to use [tsrc](https://github.com/tankerapp/tsrc) as an example.

The code samples are taken from its source code (and sometimes simplified a bit for the purpose of this article).

In a nutshell, `tsrc` is a command line tool that helps you deal with multiple repositories and also contains some functionality to interact with GitLab.

There are about 2000 lines of Python code in this project, and it's used in three different ways:

* The production code: what is executed when you type `tsrc` command
* The tests: what is executed when automatic tests run
* A library: we have C.I scripts written in Python that re-use some of `tsrc` code. (For instance, to reset all the repositories to the correct branch when trying to build a pull request)

Our goal is to find a way to properly handle errors in these three contexts.


## Hierarchy of errors

A somewhat established practice among Python programmers is to define a base class for all exceptions raised by their own project.

Usually the class name ends up in "Error". `tsrc` does not deviate from this route:

```python
# in tsrc/errors.py

class Error():
    def __init__(self, *args):
        super().__init__(self, *args)
        self.message = " ".join(str(x) for x in args)

    def __str__(self):
        return self.message
```

Things to note here:

* We define a `__str__` method so that errors look nice when printed. This will matter a lot when we'll tackle error reporting
* The base class is called `Error`. It's already in a `tsrc.errors` namespace, so there's no need for a name with a prefix like `TsrcError`. [^2]

Next, we have a few custom classes inheriting from `tscr.Error`:

```python

class GitCommandError(tsrc.Error):
    def __init__(self, working_path, cmd, *, output=None):


class GitLabError(tsrc.Error):
    def __init__(self, status_code, message):
        ...
```


Note how each error is constructed with a specific set of attributes.

If a `git` command fails, you'll need to know about working directory, the exact command that was run and the output of the command (if you captured it).

And it's the same with the `GitLabError`: you'll want to know about the HTTP status code and the content of the response when a request to the GitLab API fails.



## When to throw

Let's look at a specific example: the `tsrc sync` command.

It's a command that synchronizes all the repositories of the current workspace.

While writing the implementation of this command, there are errors we can expect to happen:

 * The network is down, so all calls to `git fetch` fail
 * Some of the repositories are dirty, so calls to `git merge` fail
 * ...
 * and so on.

And they are errors we *don't* expect to happen:

 * A SyntaxError
 * An IndexError because we used `my_list[3]` and the list only has two elements
 * An AssertionError because we triggered an `assert` failure
 * An error in a third-party library we forgot to catch

So here's the rule we've followed in `tsrc`: *every time* an error occurs that we expect, we throw a derived class of `tsrc.Error`.

So for instance, instead of letting `CalledProcessError` un-caught when we run `git` commands, we make sure to use our own `GitCommandError` class:

```python
def run_git(working_dir, *cmd):

    process = subprocess.run(cmd, cwd=working_dir)

    if process.returncode != 0:
        raise GitCommandError(working_dir, cmd)
```


It means that exceptions raised in `tsrc` are not "exceptional", in the sense they can occur even during "normal" usage.

It also means that if an error that does _not_ inherit from `tscr.Error` is raised, there's probably a bug in our production code.


## The main() wrapper

The distinction between "expected" and "unexpected" errors is made clear in the `main()` entry point of `tsrc`:

```python
def main_func():
    """ Deals with command-line arguments
    and calls appropriate functions
    """

def main():
    try:
        main_func()
    except tsrc.Error as e:
        # "expected" failure, display it and exit
        if e.message:
            print("Error:", e.message)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Thus the program can terminates in the following ways:

* A `tscr.Error` instance has been raised and un-caught: display its message if it's not empty and exit with non-zero return code.
* An other kind of exception has been raised and we did not caught it: let the program crash.
* Someone called `sys.exit()`: just terminates as the caller expects it.

Thus, as long as we take care of how we construct the instances of the `tsrc.Error` classes we raise, the end user will have a nice error message telling him what happened.

For instance:

```python
def load_manifest();
    ....
    raise tsrc.Error("Invalid manifest file ...")

def main_sync():
    ...
    load_manifest()
```

```bash
$ tsrc sync
Error: Invalid manifest file
```

Note how the backtrace will be hidden.

On the other hand, if we have an other kind of exception raised, a backtrace *will* get printed and that will allow us to investigate the bug.


## Error handling in CI scripts

We can use exactly the same technique when writing CI code.

In our case, the consumers of our script will be the developers reading the output of the pipeline, trying to figure out why there merge request was denied.

So it's crucial we handle errors correctly.

The good news is that we *also* have "expected" failures such has the code failing to compile, or the tests failing, and we have "unexpected" failures such as the network going down, or the script itself being buggy.

Hence we can re-use the same technique, where `notify()` is the function that takes care of telling the developer about the outcome of the build (via an e-mail, or with a comment on the merge request):

```python
class BuildFailed(CIError):
    ...

class TestsFailed(CIError):
    ...

def notify(message):
    ...

def ci():
    fetch_sources()
    build()
    run_tests()

def main():
    try:
      ci()
    except BuildFailed:
        notify("build failed")
    except TestsFailed:
        notify("tests failed")
    except Exception as e:
        print_bactkrace()
        notify("build scripts may be broken! Ask help from a build farm guru")
    notify("Pipeline suceeded. Congrats")
```

Note: this has nothing to do with `tsrc` itself, but I thought it was a good idea to tell you about CI scripts, too :)

## Using tsrc as a library

Since we have such a nice error hierarchy, and that every type of error contains easily accessible information as attributes of the class, callers of `tsrc` functions have a lot of liberty when trying to handle errors.

They can do very fine-grained error handling, like this:

```python
try:
    push_action = tsrc.PushAction()
    push_action.accept_merge_request()
except tsrc.GitLabError as error:
    if error.status_code == 405:
        # GitLab denied the merge request
```

They can catch only `tsrc.Error` errors (since other types indicate a bug), and re-raised their own type:

```python
try:
    push_action = tsrc.PushAction()
    push_action.accept_merge_request()
except tsrc.Error as error:
    raise FooError()
```

Or they can just ignore errors entirely and let callers of their code dealing with the errors.


## Testing error handling

Since the type, the error message, and the attributes of our exceptions is so important, we ought to test them.

With `pytest` we can write code like this:

```python
import pytest

def test_reading_config_file():
    with pytest.raises(InvalidConfigError) as e:
        tsrc.config.read_config("nosuchfile")
    assert e.value.path == "nosuchfile"
```

Note that `pytest` returns an `ExceptionInfo` instance wrapping the original exception, so we have to use the `.value` attribute. [^3]

We can also check the return code of the various commands like so:

```python

def test_sync_with_errors(tsrc_cli):
    # Arrange a workspace where a branch has diverged
    ...

    # Call the sync script:
    with pytest.raises(SystemExit) as e:
        main_sync()

    # Ensure it has failed
    assert e.value.code != 0
```

# Conclusion

Good error handling is quite easy in Python once you apply the techniques I have described here.

They all look quite simple, but it took me quite some time to discover them, so I hope you'll find them useful.

Cheers!

[^1]: The full list is in the [documentation](https://docs.pytest.org/en/latest/usage.html)
[^2]: This anti-pattern is so common that it has a name: "The Smurf Naming Convention"
[^3]: More info in [pytest documentation](https://docs.pytest.org/en/latest/assert.html#assertions-about-expected-exceptions)
