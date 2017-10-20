---
slug: "pytest-rocks"
date: "2016-04-16T13:53:51+00:00"
draft: false
title: "pytest rocks"
tags: [python, testing]
---

Today I thought I'd share my experience with various test tools for the Python
programming language.

<!--more-->

I was maintaining a Python tool that did a lot of `subprocess` calling, reading
and writing files. This kind of code is not easy to test. My solution to this
problem was to create a lot of temporary directories, so that I could exercise
the code under test safely, without interfering with the rest of my filesystem.
Also, temporary directories are created empty, which is a good way to isolate
tests from each other.
(No files read or created by `test_one` in `/tmp/test_one` can interfere with
`test_two` running in `/tmp/test_two`)

# Using unittest

I naturally started with `unittest`, which is in the standard library. (Note:
this was a long time ago, `unittest` did many progress since then)

## Basic test with a temporary directory

This is what the code looked like:

```python

# in test_one.py

import unnitest

class TestOne(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tmpfile.mkdtemp("test-one-")

    def test_one(self):
        # do stuff in self.tmpdir
        rc = ...
        self.assertEquals(rc, 0)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


# in run_tests.py

import unittest

TESTCASES = [
    TestOne,
    # ....
]

suite = unittest.TestSuite()
for test_case in TEST_CASES:
    suite.addTests(unittest.makeSuite(test_case))
runner = unittest.TextTestRunner()
result = runner.run(suite)
if not result.wasSuccessful():
    sys.exit(1)
```

## Sharing fixtures

Also, I had tests that shared a common set up and tear down. I found two
solutions, but neither was really satisfying:

* Write some helper methods like `setup_foo` in a `test_helper` module
* Or write a class containing `setup_foo` and subclass it in the other tests

So in the end there was a lot of code duplication among tests...

## Problems with unittest

* A  **lot** of boilerplate.
* The API is taken from `JUnit`, a framework written for the Java programming
  language and it just does not feel like "pythonic".
* The setup and the tear down of the tests are in two different places, so it's
  easy to forget to cleanup the temp directory in the `tearDown()` method
* The API does not conform to the PEP8 style
* There's no way to skip tests (This was fixed in Python 3.1)
* There's now way to discover tests (fixed in Python 3.2)

The last two points illustrate a fundamental problem with `unittest`: since
it's part of the standard library, you are stuck with the version coming with
your Python installation, and you cannot get new features without upgrading
Python too.

Yes, I know `unittest2` exists, but if you're going to use an external package
to run the tests, why stick with `unittest`?

# Switching to pytest

Before diving into `pytest` specific features, let me point out that **pytest is
+fully compatible with unittest**, so if you want to switch, you don't have to rewrite
+all your tests right away :)

## Basic test

Here's what the same code looks like when using `pytest`


```python

def test_one(tmpdir):
      # do stuff in tmpdir
      rc = ....
      assert rc == 0
```

Well, that's nicer isn't it?

* No boiler plate: tests functions are automatically discovered.
* No special methods for asserting: `assertEquals`, `assertTrue`,
  `assertContains` and the like are all replaced by a simple `assert`. But then
  `pytest` does some black magic and you still get nice error messages:

```text
file test_foo.py, line 1
    def test_foo():
        actual = "foo" + "bar"
        expected = "fooBar"
>       assert actual == expected
E       assert 'foobar' == 'fooBar'
E         - foobar
E         ?    ^
E         + fooBar
E         ?    ^

test_foo.py:4: AssertionError
```

* `tmpdir` is already a predefined _fixture_. The whole list is
  [here](https://pytest.org/latest/builtin.html#builtin-fixtures-function-arguments)

## Sharing fixtures

The nice thing about `pytest`is that the code of the "fixtures" (the setup /
tear down) is completely separated from the code that exercise the production
code.

`pytest` encourages you to write them in a special file called `conftest.py`.
Sharing fixtures is then as easy as writing a function, decorate it with
`@pytest.fixture` and then pass it as parameter to whatever function needs it.

Here's an example:

```python
# in conftest.py

import pytest

@pytest.fixture
def db():
    connection = DataBaseConnection("...")
    yield connection
    connection.close()

# in test_one

def test_one(db):
    # ...

# in test_two

def test_two(db):
    # ...

```

Note how the code that deals with closing the connection to the database is
right next to the code that opens it, and how `pytest` uses the `yield` keyword
to stop executing the fixture code while the test is running.

Also note how the tests do not care where the database come from: they just use
it as a parameter. (This is Dependency Injection at its finest)

Finally, by default fixtures have a scope of "function" (meaning the database
will be opened and then closed for each test function), but you can chose to
have a "module scope"  or even a "session scope".

(This is quite hard to do with `unittest`)

You can even have fixtures that are always implicitly called, by using
`autouse=True` in the fixture definition.

## Customizing pytest

You can also extend the command line API: this is especially useful if you
need some kind of token to run your tests.

Here's an example:

```python

# in conftest.py
import pytest

def pytest_addoption(parser):
    parser.addoption("--token", action="store", help="secret token")

# in test_foo.py

def test_foo(request):
     token = request.config.getoption("--token")

```

Again, this is quite hard to do with `unittest`

## Awesome plugins

Last but not least, there are a lot of plugins available to use with `pytest`.

Here are a few:

* [pytest-sugar](https://pypi.python.org/pypi/pytest-sugar) prettier output, show failures instantly
* [pytest-cache](https://pypi.python.org/pypi/pytest-cache) allow to run only
  the tests that failed in the previous run with `--lf` (note: included in
  `pytest core` since 2.8)
* [pytest-xdist](https://pypi.python.org/pypi/pytest-xdist) run tests in parallel, or even distribute them over the network
* [pytest-cov](https://pypi.python.org/pypi/pytest-cov) measure code coverage

You can even use `pytest` with tests written in C++ using `gtest` or
`boost::test` thanks to the [pytest-cpp](
https://github.com/pytest-dev/pytest-cpp) plugin
