---
authors: [dmerej]
slug: python-tests-tips
date: 2020-04-25T14:20:47.807992+00:00
draft: false
title: Tips for better Python tests
tags: [python, testing]
summary: Improve your Python tests with these simple tips
---

Today, I'd like to share with you a list of small tips to help you write better tests when using Python. No that the tips often improve both the readability of the test implementation, *and* of the failure messages (which is pretty important too).

# Use pytest

Pytest does a great job in generating very good error messages from your assertions, without the need for anything other than the `assert` statement.

Take this assertion for instance:

```python
assert foo(x) == bar(y)
```

Here's what the failure will look like when using `pytest` if the assertion fails:

```
    def test_foobar():
        x = 2
>       assert foo(x) == bar(x)
E       assert 4 == 5
E        +  where 4 = foo(2)
E        +  and   5 = bar(2)

test.py:11: AssertionError
```

Note how much information you get about what went wrong, like the entire body of the function up to the assertion that failed,or when the values that were compared came from.

It gets even better - take this other assertion:

```python
assert get_message() == "this is what I expected"
```

And note the nice, detailed diff between the two strings that gets printed:

```
    def test_get_message():
>       assert get_message() == "this is what I expected"
E       AssertionError: assert 'this is what I expected' == 'this is what I got'
E         - this is what I expected
E         ?                ^^^^^ --
E         + this is what I got
E         ?                ^^^
```

# A more complex example

For the rest of this post, let's assume you are testing a `sync_folders()` function that can synchronize a remote folder with a local one.

Here's one of the tests you wrote:

```python
def test_can_update_local_file(remote, local):
    local_file  = local / "a.txt"
    local_file.write_text("old contents")
    new_contents = "new contents"
    remote.add_file("a.txt", contents=new_contents)

    sync_folders(remote, local)

    actual_contents = local_file.read_text()
    assert actual_contents == new_contents
```

_Side note: I usually split my tests into three *arrange* /*act* / *assert* parts and I visualize them using vertical space (this tip is free)_.

# Add context to assertions

Did you know you can add a string at the end of the `assert` statement?

```diff
def test_sync(remote, local):
    ...

    actual_contents = local_file.read_text()
-   assert actual_contents == new_contents"
+   assert actual_contents == new_contents, "a.txt should have been updated"
```

This way, instead of having to read this:

```
E       AssertionError: assert 'old contents\n' == 'new contents'
E         - old contents
E         + new contents

```

you get that:

```
>       assert actual_contents == new_contents, "a.txt should have been updated"
E       AssertionError: a.txt should have been updated
E       assert 'old contents\n' == 'new contents'
E         - old contents
E         + new contents
```

# Reduce noise

You can also improve the signal over noise ratio by using `pytest.fail` instead of the `assert` statement:

```diff
-  assert actual_contents == new_contents", "a.txt should have been updated"
+  if actual_contents != new_contents:
+      pytest.fail("a.txt should have been updated")
```

```
        if actual_contents != new_contents:
>           pytest.fail("a.txt should have been updated")
E           Failed: a.txt should have been updated```
```

Be careful when using this technique, because it may hinder the debugging of failing tests.

# Use custom assertion helpers

Finally, don't hesitate to factorize code about assertions, for instance in a `test/helpers.py` file:

```python
def assert_was_updated(path, contents):
    ...

def assert_was_created(path):
    ...

# and so on
```
# Use docstrings to describe tests scenarios

This is my favorite tip ever: if you are testing something complex, *add a human-readable description* of the test inside the doc string.

Still using our `test_can_update_local_file` example:

```python
def test_can_update_local_file():
    """ Scenario:
    * Create a file named a.txt in the local folder with
      "old" contents
    * Add a new version of the `a.txt` file in the remote folder
    * Synchronize the remote and local folders
    * Check that `a.txt` has been updated
    """
    ....
```

There are two advantages with this approach:

* It can be helpful to have a human readable description of what the test is supposed to be doing when reading the implementation of the code - like any docstring
* Since pytest displays the entire block of the function block that caused the assertion to fail, you get a reminder of what the test was about when reading the failure message.

# Reflections on the last tip

You can stop reading there if you want, but I thought it would be interesting to know how I end up using docstrings in my test code - especially since for a long time, I was convinced that docstrings were useless if the test implementation was clear enough[^1]!

What changed my mind? In two words: **code review**. let me elaborate.

## Getting feedback

I've had the chance to get my Python test code reviewed by some team mates who did not know pytest very well but were used to frameworks like Mocha or Cucumber. They help me realize this simple truth: using only function names and implementation (in other words, *code*) to express all the subtlety of what the tests are about *cannot* be enough - kind of obvious when you say it like that, right?

But in this case code review can only see you _what_ needs to be improved, but
not always _how_.

So I did what I had to: I took a closer look on those other frameworks.

## Getting to know other frameworks

Here's an implementation of our test using [Mocha](https://mochajs.org/):

```Javascript
describe('sync', function() {
  it('syncs a remote file', function() {
    remote.addFile('a.txt', { contents: newContents });

    syncFolders(remote, local);

    const actualContents = local.join('a.txt').readText();
    assert.equal(actualContents, newContents);
  });
});
```

And here's an implementation using [Cucumber](https://cucumber.io):

```gherkin
# in synchronization.feature
Feature: Synchronization

Scenario: file updated remotely
  Given there is a local file 'a.txt' containing "old_contents"
  Given there is a remote file 'a.txt' containing "new_contents"
  When I synchronize the folders
  Then the local file a.txt contains "new_contents"
```

```ruby
# in synchronization.rb
Given(/there is a local file '{word}' containing "{string}"/ do |path, contents|
  open(path, 'w') do |f|
      f.puts contents
  end
end

When(/I synchronize the folder/) do
  sync_folders(@local, @remote)
end

# ...
```

Quite different styles, right?

## Finding a middle ground

And there you have it: I came up with using docstrings with pytest because it was a nice middle ground between those two approaches.

* In Mocha, you usually write short text in `it()` and `describe()` - rarely several lines, but with docstrings the description can be as long as you need.

* In Cucumber, your English text is in a different file than your supporting code and has to follow some kind of custom syntax, but with docstrings you can have no constraints at all for the formatting of your description, and it lives right next to the accompanying code


## Conclusion

So what did we learn?

* Being reviewed helps keeping your code readable - but you already knew that, right?
* Exploring new languages and frameworks gives you insights on how to improve your code
* If you are in a team that contains people who use different languages and frameworks than yours and you get them to review your code, it will lead to even better code because you'll be combining the two effects from above!

In other terms, consider increasing the diversity of your teams, and don't hesitate to explore new things 😎.

[^1]: I also believed good code did not need comments - fortunately, I read [this article](https://hackaday.com/2019/03/05/good-code-documents-itself-and-other-hilarious-jokes-you-shouldnt-tell-yourself).
