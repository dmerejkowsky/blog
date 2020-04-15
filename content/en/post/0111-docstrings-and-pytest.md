---
authors: [dmerej]
slug: docstrings-and-pytest
date: 2020-04-15T16:43:47.807992+00:00
draft: true
title: "An exploration of various test frameworks"
tags: [python]
summary: Improve your tests readability with this simple change
---

# Introduction

Let's start this blog post by examining a few different tests frameworks - we'll
come back to `pytest` afterwards.

## JUnit

JUnit is a test framework for Java

```java

```

## RSpec

Let me say this : `rspec` is one of the best test frameworks ever. Tests written in rspec look like this:

```ruby
RSpec.describe "user storage" do
  before(:each) do
    @db = connect_db()
    @db.create!
  end

  after(:each) do
    @db.destroy!
  end

  it "can retrieve users from the db using their id" do
    id = @db.add_user("Jane")
    user = @db.get_user_by_id(id)
    expect(user.name).to eq("Jane")
  end
end
```

Notice how little difference there is between the code as written in Ruby
and how you will describe the feature of the `DB` class in plain English -
it's just wonderful.

It's output looks like this by default:


```
.
Finished in 0.00212 seconds (files took 0.07689 seconds to load)
1 example, 0 failures
```

But you can use the `documentation` format instead:

```
user storage
  can retrieve users from the db using their id

Finished in 0.00122 seconds (files took 0.07726 seconds to load)
1 example, 0 failures
```

## Mocha

Mocha is a test framework for JavaScript

Here's what the same example looks like:

```javascript
describe("user storage", function() {
  let db;

  beforeEach(function() {
   db = connect_db();
   db.create();
  });

  afterEach(function() {
    db.destroy();
  });

  it("can retrieve users from the db using their id", function() {
    const id = db.addUser("Jane");
    const user = db.getUserById(id);
    assert.equal(user.name, "Jane");
  });

});
```

It's output looks like this by default:

```
  user storage
    ✓ can retrieve users from the db using their id can retrieve users from the db using their id
```

Notice how `mocha` and `rspec` are similar. The `mocha` framework cannot really have a DSL ala Ruby,
but you still get this feeling that you are reading documentation, not test code (if you squint and forget
about all these `});`

# pytest

Pytest is *the* test framework for Python. There's a `unittest` package in the standard library but I won't
describe it here because it's quite similar to the JUnit framework. Both RSpec and JUnit have served
as inspiration for test authors.

To me, what makes`pytest` great is that it cares very little about what
other test framework do, and more about how to make the tests as *pythonic*
as possible.

Here's how the example we used throughout looks like:


```python
@pytest.fixture
def db():
    db = connect_db()
    db.create()
    yield db
    db.destroy()


def test_get_user_by_id(db):
    id = db.add_user("Jane")
    user = db.get_user_by_id(id)
    assert user.name == "Jane"
```

Notice how it does *not* read like a specification - it looks like boring code (and
that's one of the reasons I personally love it)

Notice how the fixture is completly separated from the test code, and how the
`tearDown` part is right after the `setupPart` - in fact, in the *same* function.

Also, not that it uses that it uses lots of Python features like decorators
and generators with `yield` statements.

But really, the whole `fixture` thing works because Python as:

* No overload
* Named and positional parameters
* Lots of feature around introspection
.. and so on


Its output looks like this:

```
============================= test session starts ==============================
platform linux -- Python 3.8.2, pytest-5.3.2, py-1.8.0, pluggy-0.13.1
rootdir: /home/dmerej/work/pytest-docstrings
collected 1 item

test.py .                                                                [100%]

============================== 1 passed in 0.01s ===============================
```

# When it fails

But it's a bit silly to only consider the "all tests have pass" output, don't you
think ?

After all, you'll really need to read the output if some of the tests have fail, right?

That's where things start to get interesting.
