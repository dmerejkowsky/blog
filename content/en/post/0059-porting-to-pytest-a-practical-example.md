---
authors: [dmerej]
slug: porting-to-pytest-a-practical-example
date: 2018-03-01T16:34:19.584239+00:00
draft: false
title: "Porting to pytest: a practical example"
tags: [python, testing]
---

# Introduction

The other day I was following the [django tutorial](https://docs.djangoproject.com/en/2.0/intro/).

If you never read the tutorial, or don't want to, here's what you need to know:

We have a django project containing an application called `polls`.

We have two model objects representing questions and choices.

Each question has a publication date, a text, and a list of choices.

Each choice has a reference to an existing question (via a foreign key), a text, and a number of votes.

There's a view that shows a list of questions as links. Each link, when clicked displays the choices and has a form to let the user vote.

The code is pretty straightforward:

```python
# polls/models.py
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def was_published_recently(self):
        now = timezone.now()
        two_days_ago = now - datetime.timedelta(days=2)
        return two_days_ago < self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

```

Everything went smoothly until I arrived at the [part 5](https://docs.djangoproject.com/en/2.0/intro/tutorial05/), about automated testing, where I read the following:

> Sometimes it may seem a chore to tear yourself away from your productive, creative programming work to face the unglamorous and unexciting business of writing tests, particularly when you know your code is working properly.

Well, allow me to retort!

# Starting point: using tests from the documentation


Here's what the tests looks like when extracted from the django documentation:

```python
import datetime

from django.utils import timezone
from django.test import TestCase

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self);
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)


    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            []
        )

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            []
        )

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [
                '<Question: Past question 2.>',
                '<Question: Past question 1.>'
            ]
        )
```

We can run them using the `manage.py` script and check they all pass:

```console
$ python manage.py test polls
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
........
----------------------------------------------------------------------
Ran 8 tests in 0.017s

OK
Destroying test database for alias 'default'...
```


OK, tests do pass. Let's try and improve them.

I've set up [a GitHub repository](https://github.com/dmerejkowsky/django-polls) where you can follow the following steps commit by commit if you wish.

# Step one: setup pytest

I've already told you [how much I love pytest]({{< ref "/post/0006-pytest-rocks.md" >}}), so let's try to convert to `pytest`.

The first step is to install `pytest-django` and configure it:

```console
$ pip install pytest pytest-django
```

```cfg
# in pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE=mysite.settings
python_files = tests.py test_*.py
```

We can now run tests using `pytest` directly:

```console
$ pytest
========== test session starts ========
platform linux -- Python 3.5.3, pytest-3.3.1, py-1.5.2, pluggy-0.6.0
Django settings: mysite.settings (from ini file)
rootdir: /home/dmerej/src/dmerej/django-polls, inifile: pytest.ini
plugins: django-3.1.2
collected 8 items

polls/tests.py ........   [100%]

======== 8 passed in 0.18 seconds =======
```

# Step two: rewrite assertions

We can now use `pytest` magic to rewrite all "easy" assertions such as `assertFalse` or `assertEquals`:

```patch
- self.assertFalse(future_question.was_published_recently())
+ assert not future_question.was_published_recently()
```

Already we can see several improvements:

* The code is more readable and follows PEP8
* The error messages are more detailed:

```console
# Before, with unittest
$ python manage.py test
    def test_was_published_recently_with_future_question(self):
        ...
>       self.assertFalse(question.was_published_recently())
E       AssertionError: True is not false

# After, with pytest
$ pytest
>       assert not question.was_published_recently()
E       AssertionError: assert not True
E        +  where True = <bound method was_published_recently() of Question>
```

Then we have to deal with `assertContains` and `assertQuerysetEqual` which look a bit django-specific.

For `assertContains` I quickly managed to find I could use `response.rendered_content` instead:


```patch
- self.assertContains(response, "No polls are available.")
+ assert "No polls are available." in response.rendered_content
```

For `assertQuerysetEqual` it was a bit harder.

```python
def test_past_question(self):
    create_question(question_text="Past question.", days=-30)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(
        response.context['latest_question_list'],
        ['<Question: Past question.>']
    )
```

This test checks that the context used to generate the response was passed correct `latest_question_list` value.

But it does so by checking the *string representation* of the `Question` object.

Thus, it will break as soon as `Question.__str__` changes, which is not ideal.

So instead, we can write something like this and check for the content of the `question_text` attribute directly:


```python
def test_past_question(self):
    create_question(question_text="Past question.", days=-30)
    response = self.client.get(reverse('polls:index'))
    actual_questions = response.context['latest_question_list']
    assert len(actual_questions) == 1
    actual_question = actual_questions[0]
    assert actual_question.question_text == "Past question"

```

While we're at it, we can introduce small helper functions to make the tests easier to read:


For instance, the string `No polls are available` is hard-coded twice in the tests. Let's introduce a `assert_no_polls` helper:

```python
def assert_no_polls(text):
    assert "No polls are available" in text
```

```patch
- assert "No polls are available." in response.rendered_content
+ assert_no_polls(response.rendered_content)
```

An other hard-coded string is `polls:index`, so let's introduce `get_latest_list`:

```python
def get_latest_list(client):
    response = client.get(reverse('polls:index'))
    assert response.status_code == 200
    return response.context['latest_question_list']
```
Note how we embedded the status code check directly in our helper, so we don't have to repeat the check in each test.

Also, note that if the name of the route (`polls:index`) or the  name of the context key used in the template (`latest_question_list`) ever changes, we'll just need to update the test code in one place.

Then, we can further simplify our assertions:

```python
def assert_question_list_equals(actual_questions, expected_texts):
    assert len(actual_questions) == len(expected_texts)
    for actual_question, expected_text in zip(actual_questions, expected_texts):
        assert actual_question.question_text == expected_text

def test_past_question(self):
    ...
    create_question(question_text="Past question.", days=-30)
    latest_list = get_latest_list(self.client)
    assert_question_list_equals(latest_list, ["Past question."])
```


# Step three: move code out of classes

The nice thing about `pytest` is that you don't need to put your tests as methods of a class, you can just write
test functions directly.

So we just remove the `self` parameter, indent back all the code, and we are (almost) good to go.

We already got rid of all the `self.assert*` methods, so the last thing to do is pass the Django test client as a parameter instead of using `self.client`. (That's how [pytest fixtures](https://docs.pytest.org/en/latest/fixture.html) work):

```patch
-    def test_two_past_questions(self):
-        ...
-        latest_list = get_latest_list(self.client)

+ def test_no_questions(client):
+    latest_list = get_latest_list(client)

```

But then we encounter an unexpected failure:

```
Polls/tests.py:34: in create_question
    return Question.objects.create(question_text=question_text, pub_date=time)

    ...

>       self.ensure_connection()
E       Failed: Database access not allowed, use the "django_db" mark, or the "db" or "transactional_db" fixtures to enable it.
```

Back when we used `python manage.py test`, django's `manage.py` script was implicitly creating a test database for us.

When we use `pytest`, we have to be explicit about it and add a special marker:

```python
import pytest

# No change here, no need for a DB
def test_was_published_recently_with_old_question():
    ...

# We use create_question, which in turn calls Question.objects.create(),
# so we need a database here:
@pytest.mark.django_db
def test_no_questions(client):
    ...
```

True, this is a bit annoying, but note that if we only want to test the models themselves (like the `was_published_recently()` method), we can just use:

```console
$ pytest -k was_published_recently
```

and no database will be created *at all*.

# Step four: Get rid of doc strings

I don't like doc strings, *except* when I'm implementing a very public API. There, I've said it.

I very much prefer when the code is "self-documenting", *especially* when it's test code.

As [Uncle Bob](http://blog.cleancoder.com) said, "tests should read like well-written specifications". So let's try some refactoring.

We can start with more meaningful variable names, and have more fun with the examples:

```patch
def test_was_published_recently_with_old_question():
-   time = timezone.now() - datetime.timedelta(days=1, seconds=1)
-   old_question = Question(pub_date=time)
+   last_year = timezone.now() - datetime.timedelta(days=365)
+   old_question = Question('Why is there something instead of nothing?',
+                            pub_date=last_year)
    assert not old_question.was_published_recently()

def test_was_published_recently_with_recent_question():
-   time = timezone.now() - datetime.timedelta(days=1, seconds=1)
-   recent_question = Question(pub_date=time)
+   last_night = timezone.now() - datetime.timedelta(hours=10)
+   recent_question = Question('Dude, where is my car?', pub_date=last_night)

```

Time and date code is always tricky, and a negative number of days does not really make sense, so let's make things easier to reason about:

```python
def n_days_ago(n):
    return timezone.now() - datetime.timedelta(days=n)


def n_days_later(n):
    return timezone.now() + datetime.timedelta(days=n)

```

Also `create_question` is coupled with the `Question` model, so let's use the same names for the parameter names and the model's attributes.

And since we may want to create question without caring about the publication date, let's make it an optional parameter:

```python
def create_question(question_text, *, pub_date=None):
    if not pub_date:
        pub_date = timezone.now()
    ...
```

Code becomes:

```patch
-    create_question(question_text="Past question.", days=-30)
+    create_question(question_text="Past question.", pub_date=n_days_ago(30))
```

Finally, let's add a new test to see if our helpers really work:

```python

@pytest.mark.django_db
def test_latest_five(client):
    for i in range(0, 10):
        pub_date = n_days_ago(i)
        create_question("Question #%s" % i, pub_date=pub_date)
    latest_list = get_latest_list(client)
    assert len(actual_list) == 5
```

Do you still think this test needs a docstring ?


# Step five: fun with selenium

## Selenium basics

[Selenium](https://www.seleniumhq.org/) deals with browser automation.

Here we are going to use the Python bindings, which allow us to start `Firefox` or `Chrome` and control them with code.

(In both cases, you'll need to install a separate binary: `geckodriver` or `chromedriver` respectively)


Here's how you can use `selenium` do visit a web page and click the first link:

```python
import selenium.webdriver

driver = selenium.webdriver.Firefox()
# or
driver = selenium.webdriver.Chrome()
driver.get("http://example.com")
link = driver.find_element_by_tag_name('a')
link.click()
```


## The Live Server Test Case

Django exposes a `LiveServerTestCase`, but no `LiveServer` object or similar.

The code is a bit tricky because it needs to spawn a "real" server in a separate thread, make sure it uses a free port,  and tell the selenium driver to use an URL like `http://localhost:32456`

Fear not, `pytest` also works fine in this case. We just have to be careful to use `super()` in the set up and tear down methods so that the code from `LiveServerTestCase` gets executed properly:

```python
import urllib.parse


class TestPolls(LiveServerTestCase):
    serialized_rollback = True

    def setUp(self):
        super().setUp()
        self.driver = selenium.webdriver.Firefox()

    def tearDown(self):
        self.driver.close()
        super().tearDown()

    def test_home_no_polls(self):
        url = urllib.parse.urljoin(self.live_server_url, "/polls")
        self.driver.get(url)
        assert_no_polls(self.browser.page_source)

```

If you're wondering why we need `serialized_rollback=True`, the answer is in [the documentation](https://docs.djangoproject.com/en/2.0/topics/testing/tools/#transactiontestcase). Without it we may have weird database errors during tests.

Our first test is pretty basic: we ask the browser to visit the `'polls/` URL and check no polls are shown, re-using our `assert_no_polls` helper function from before.

Let's also check we are shown links to the questions if they are some, and can click on them:


```python
class TestPolls(LiveServerTestCase):
    ...
    def test_home_list_polls(self):
        create_question("One?")
        create_question("Two?")
        create_question("Three?")
        url = urllib.parse.urljoin(self.live_server_url, "polls/")
        self.driver.get(url)
        first_link = self.driver.find_element_by_tag_name("a")
        first_link.click()
        assert "Three?" in self.driver.page_source
```


## Let's build a facade

The `find_element_by_*` methods of the selenium API are a bit tedious to use: thery are called `find_element_by_tag_name`, `find_element_by_class_name`, `find_element_by_id` and so on

So let's write a `Browser` class to hide those behind a more "Pythonic" API:

```python
# old
link = driver.find_element_by_tag_name("link")
form = driver.find_element_by_id("form-id")

# new
link = driver.find_element(tag_name="link")
form = driver.find_element(id="form-id")
```

(This is known as the "facade" design pattern)


```python
class Browser:
    """ A nice facade on top of selenium stuff """
    def __init__(self, driver):
        self.driver = driver

    def find_element(self, **kwargs):
        assert len(kwargs) == 1   # we want exactly one named parameter here
        name, value = list(kwargs.items())[0]
        func_name = "find_element_by_" + name
        func = getattr(self.driver, func_name)
        return func(value)

```

Note how we have to convert the `items()` to a real list just to get the first element... (In Python2, `kwargs.items()[0]` would have worked just fine). Please tell me if you find a better way ...

Note also how we *don't* just inherit from `selenium.webdriver.Firefox`. The goal is to expose a *different* API, so using composition here is better.

If we need access to attributes of `self.driver`, we can just use a property, like this:

```python
class Browser

    ...

    @property
    def page_source(self):
        return self.driver.page_source
```

And if we need to call a method directly to the underlying object, we can just forward the call:

```python
    def close(self):
        self.driver.close()
```


We can also hide the ugly `urllib.parse.urljoin(self.live_server_url)` implementation detail:


```python

class Browser:
    def __init__(self, driver):
        self.driver = driver
        self.live_server_url = None  # will be set during test set up

    def get(self, url):
        full_url = urllib.parse.urljoin(self.live_server_url, url)
        self.driver.get(full_url)


class TestPolls(LiveServerTestCase):

    def setUp(self):
        super().setUp()
        driver = selenium.webdriver.Firefox()
        self.browser = Browser(driver)
        self.browser.live_server_url = self.live_server_url
```

Now the test reads:

```python

    def test_home_no_polls(self):
        self.browser.get("/polls")
        assert_no_polls(self.browser.page_source)
```

Nice and short :)

## Launching the driver only once

The `setUp()` method is called before each test, so if we add more tests we're going to create tons of instances of Firefox drivers.

Let's fix this by using `setUpClass` (and not forgetting the `super()` call)


```python
class TestPolls(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        driver = webdriver.Chrome()
        cls.browser = Browser(driver)

    def setUp(self):
        self.browser.base_url = self.live_server_url

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        super().tearDownClass()

```

Now the `browser` is a *class attribute* instead of being an *instance attribute*. So there's only one `Browser` object for the whole test suite, which is what we wanted.

The rest of the code can still use `self.browser`, though.


## Debugging tests

One last thing. You may think debugging such high-level tests would be painful.

But it's actually a pretty nice experience due to just one thing: the built-in Python debugger!

Just add something like:

```python

def test_login():
    self.browser.get("/login")
    import pdb; pdb.set_trace()
```

and then run the tests like this:

```console
$ pytest -k login -s
```

(The `-s` is required to avoid capturing output, which `pdp` does not like)

And then, as soon as the tests reaches the line with `pdb.set_trace()` you will have:

* A brand new Firefox instance running, with access to all the nice debugging tools (so you can quickly find out things like ids or CSS class names)
* ... and a nice REPL where you'll be able to try out the code using `self.browser`

By the way, the REPL will be even nicer if you use [ipdb](https://pypi.python.org/pypi/ipdb) or [pdbpp](https://pypi.python.org/pypi/pdbpp/) and enjoy auto-completion and syntax coloring right from the REPL :)

# Conclusion

I hope I managed to show that you actually *can* get creative writing tests, and even have some fun.

See you next time!
