---
slug: porting-to-pytest-a-practical-example
date: 2018-03-01T16:34:19.584239+00:00
draft: true
title: "Porting to pytest: a practical example"
tags: [python, test]
---

# Introduction

The other day I was following the [django tutorial](https://docs.djangoproject.com/en/2.0/intro/).

If you never read the tutorial, or don't want to, here's what you need to know:

We have a django project containing an application called `polls`.

We have two model objects representing question and choice.

Each question has a publication date, a text, and a list of choices.

Each choice has a reference to an existing question (via a foreign key), a text, and a number of votes.

There's a view that shows a list of questions as links. Each link, when clicked displays the choices and has a form to let the user vote.

The code is pretty straightforward:

```python
# models
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

Let's try and improve those tests.

# Step one: setup pytest

I've already told you [how much I love pytest]({{< ref "post/2016-04-16-pytest-rocks.md" >}}), so let's try to convert to `pytest`.

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

# Step two: rewrite assertions

We can now use `pytest` magic to rewrite all "easy" assertions such as `assertFalse` or
``assertEquals``:

```patch
- self.assertFalse(future_question.was_published_recently())
+ assert not future_question.was_published_recently()
```

Already we can see several improvements:

* The code is more readable and follow PEP8
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
- assert "No polls are available." in response.rendered_content
+ self.assertContains(response, "No polls are available.")
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

Now look at what happens when we adapt the next tests:

```python
def test_future_question(self):
    """
    Questions with a pub_date in the future aren't displayed on
    the index page.
    """
    )
```

So, we can write something more simple, and also get rid of the duplication:

```python
def get_latest_questions_list(client):
    response = client.get(reverse('polls:index'))
    return response.context['latest_question_list']


def test_past_question(self):
    create_question(question_text="Past question.", days=-30)
    actual_questions = get_latest_questions_list(self.client)
    assert len(actual_questions) == 1


def test_future_question(self):
    create_question(question_text="Future question.", days=30)
    actual_questions = get_latest_questions_list(self.client)
    assert not actual_questions == 1
```

# Move code out of classes

```
Polls/tests.py:34: in create_question
    return Question.objects.create(question_text=question_text, pub_date=time)

    ...

>       self.ensure_connection()
E       Failed: Database access not allowed, use the "django_db" mark, or the "db" or "transactional_db" fixtures to enable it.
```
