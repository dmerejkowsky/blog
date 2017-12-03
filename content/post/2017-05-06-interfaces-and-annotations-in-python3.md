---
tags: ["python"]
slug: interfaces-and-annotations-in-python3
date: 2017-05-06T12:01:19.942498+00:00
draft: false
title: Interfaces and Annotations in Python3
---

TL;DR: Annotations in Python3 are very useful when declaring interfaces
using `abc` metaclass.

If you want to stop reading here, I'm not going to stop you:)

If not, allow me to take you to on a small journey where I explain what all of this
is about ...

<!--more-->

# A Java example

Let's assume you have a `PostgreSQL` database containing employee records.
You are building a web site that will be able to display information about an
employee given its ID number.

You have a class called `SQLRepository` that allows you to fetch
employees by ID, and a `EmployeeController` class with a `viewEmployee`
method will be called when the user goes through the correct URL.

Lastly, you have a `Renderer` class that knows how to generate the
HTML description of your employees.

## First attempt

The most obvious way to implement the controller looks like this:

```java
package mypackage.controller;

import mypackage.Employee;
import mypackage.repository.SQLRepository;
import mypackage.renderer.Renderer;

public class Controller {
    private SQLRepository repository;
    private Renderer renderer;

    public Controller() {
        repository = new SQLRepository();
        renderer = new Renderer();
    }

    public String viewEmployee(int id) {
        Employee employee = repository.getEmployeeByID(id);
        String res = renderer.renderEmployee(employee);
        return res;
    }
}
```

But there are a few problems with this implementation.

## Testing the controller

It's going to be difficult, right?

As soon as you want to instantiate a new controller, the constructor of
`SQLRepository()` will get called too, which means you'll have to set up
a `PostgreSQL` database just so you can run the tests.

We say that the "flow of control" goes from the Controller to the SQLRepository
class, or that there is a _runtime dependency_ between the Controller and the
SQLRepository.

And since `Controller.java` contains an `import` of the `SQLRepository` class,
we say there is a _source code dependency_ between the Controller and the
SQLRepository classes.

This is where interfaces come in.


## Introducing an interface

We are going to "decouple" the Controller and the SQLRepository by introducing
an interface:


```java
// In Repository.java
public interface Repository {
    public Employee getEmployeeByID(int id);
}
```

Then, we tell `SQLRepository` to implement the interface:

```diff
+import mypackage.repository.Repository;

-public class SQLRepository {
+public class SQLRepository implements Repository {
```

And finally we pass the repository as an argument to the
Controller constructor:


```diff
-import mypackage.repository.SQLRepository;
+import mypackage.repository.Repository;
 import mypackage.renderer.Renderer;

 public class Controller {
-    private SQLRepository repository;
+    private Repository repository;
     private Renderer renderer;

-    public Controller() {
-        repository = new SQLRepository();
+    public Controller(Repository repository) {
+        this.repository = repository;
         renderer = new Renderer();
     }
```

Note the flow of control still goes from the Controller to the Repository, but
now the  `Controller.java` file no longer depends on the `SQLRepository.java` source file.

Instead, both source files now depend on the `Repository.java` interface.

This is called the "Dependency Inversion Principle".

An other way to describe the change is that we now have a _boundary_ between the
controller and the repository, and that the interface is what allows code to
cross the boundary.

Using a different implementation of the `Repository` interface, it's now
possible to test the Controller without ever touching the database:

```java
public class FakeRepository implements Repository {
    private ArrayList<Employee> employees;

    public FakeRepository() {
        employees = new ArrayList<Employee>();
    }

    public void addEmployee(Employee employee) {
        employees.add(employee);
    }

    public Employee getEmployeeByID(int id) {
        return employees.get(id);
    }
}

public class ControllerTest extends TestCase {

    // ...

    public void testViewEmployee() {
        Employee smith = new Employee("John Smith");

        FakeRepository fakeRepository = new FakeRepository();
        fakeRepository.addEmployee(smith);

        Controller controller = new Controller(fakeRepository);

        String html = controller.viewEmployee(0);
        assertEquals(html, "<span class=\"employe\">John Smith</p>");
    }

}
```

{{< note >}}
Interfaces in Java have other use than just dependency inversion, the example is
mostly here for the sake of what's coming next.
{{</ note >}}

# Same thing, with Python


Let's rewrite our first version of the Java code in Python:

```python
# First version, hard to test

from renderer import Renderer
from repository import SQLRepository

class Controller:
    def __init__(self):
        self.repository = SQLRepository()
        self.renderer = Renderer()

    def view_employee(self, id):
        employee = self.repository.get_employee_by_id(id)
        res = self.renderer.render_employee(employee)
        return res
```

Same thing, we have a source code dependency between `controller.py` and
`repository.py`.

Now, let's invert the dependency:

```text
-from repository import SQLRepository

 class Controller:
-    def __init__(self):
-        self.repository = SQLRepository()
+    def __init__(self, repository):
+        self.repository = repository
         self.renderer = Renderer()
```

Yup, that's all we have to change!

Testing with a FakeRepository is as easy as:

```python
from controller import Controller
from employee import Employee

class FakeRepository:
    def __init__(self):
        self._employees = list()

    def add_employee(self, employee):
        self._employees.append(employee)

    def get_employee_by_id(self, id):
        return self._employees[id]

def test_view_employee():
    smith = Employee("John Smith")

    fake_repository = FakeRepository()
    fake_repository.add_employee(smith)

    controller = Controller(fake_repository)

    assert "John Smith" in controller.view_employee(0)
```

So what just happened here?

We completely removed the source code dependency between the repository and the
controller.

We _did_ introduce an interface but it's hidden behind the implementation: the
interface between the controller and the repository is simply the list of
all methods sent from the controller to its repository instance.

This is also known as "Duck Typing": we can pass a walrus instead of a duck as
long as it's a quacking walrus.

{{< note >}}
You may have heard an other definition of duck typing. I find this one much more accurate.
It was coined by Avdi Grim, from [Ruby Tapas](https://rubytapas.com) fame.
{{</ note >}}

## The problem with Duck Typing

Let's assume the database schema is changed. We now have several companies in
the same database, and the ID are only unique for a given company.

This means that we will need to provide both a company name and an employee id
when querying the repository.

`getEmployeeByID` has to be renamed to just `getEmployee` and now takes
a string (the company name) and an integer (the employee id).

In the Java world, as soon as we rename the method in the `SQLRepository` class,
we'll a compilation error.

```text
SQLRepository.java:[6,8]
mypackage.repository.SQLRepository is not abstract and does not override
abstract method getEmployeeByID(int) in mypackage.repository.Repository
```

In fact, we'll get all kind of errors until we also change the `Repository` interface,
the `FakeRepository` class, the production code and the test code.

But it Python, nothing like this will happen. Our test will continue to pass, and the
production code will just crash.

```text
AttributeError: 'SQLRepository' object has no attribute 'get_employee_by_id'
```

(This, by the way, is the difference between "static" and "dynamic" typing)


There are many ways to tackle this problem:

* Write integration tests that will check what happens when boundaries are crossed.
* Use `mock.MagicMock(SQLRepository)` in order to make sure `FakeRepository`
  has the same methods as `SQLRepository`
* Use static analysis provided by a linter
* Take inspiration from statically typed languages and write an explicit `Repository` interface.

In this article we'll only talk about the last one, but please bear in mind that
the other ways can work really well too :)

Anyway, let's change the code so that both `SQLRepository` and `FakeRepository` inherit
from a `Repository` class.

How do we make sure all the methods from the interface are implemented ?

## The dark ages

A long time ago, you had to write something like this:

```python
class Repository:

    def get_employee(self, company_name, id):
        raise NotImplementedError()
```

That way, if you forget to override the `get_employee` method, you get a
`NotImplementedError` exception when the method is called.

But sometimes you _do_ have some code that is not implemented yet, and you want
to use `NotImplementedError` to signal this to the callers of your function.

How do you make the difference between a real "not implemented" error and a typo
in the name of the method you defined in the daughter class?


## Metaclass to the rescue!

Nowadays, it's better to write your interface like this:

```python
import abc

class Repository(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_employee(self, company_name, id):
        pass
```

That way, if you don't implement all the abstract methods, you'll get an error
when the daughter class is instantiated:

```text
TypeError: Can't instantiate abstract class FakeRepository with abstract methods get_employee
```

## Documenting

There's still an issue though. What if you don't call the method with the right
types, like using a string instead of an integer for the `id` parameter ?

Until not long ago, one solution was to use the docstring for this, and then use
a tool like `sphinx.autodoc` to generate nice HTML documentation:

```python
@abc.abstractmethod
def get_employee(self, company_name, id):
    """ Fetch an employee from the database

    :param company_name: name of the company
    :param id: ID of the employee in the company
    :type company_name: string
    :type id: int
    :returns: an `Employee` instance

    """
    pass
```

I don't know about you, but I don't find this really readable.

In fact, there are at least two other ways to document the parameters names and
types:

```python
# Numpy style
def get_employee(self, company_name, id):
    """ Fetch an employee from the database

    Parameters
    ----------
    company_name : str
      Name of the company
    id : integer
      ID of the employee

    Returns
    -------
    An Employee instance
    """

# Google style:
def get_employee(self, company_name, id):
    """ Fetch an employee from the database

    Args:
      company_name : name of the company as a string
      id : id of the employee as an integer
    Returns:
      An employee instance
    """
```

But in every case, you have to spell the name of the arguments twice: once in
the definition of the function, and once in the docstring.

## Annotations to the rescue!

Annotations are a Python feature that was added in Python3.

Basically, you can use a colon after the parameter names to specify their types,
and add an arrow at the end of the definition to specify the returned type:

```python

import abc

class Repository(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_employee(self, company_name: str, id: int) -> Employee
        pass
```

I really like this solution. I find it concise, readable, and it makes it possible
to get rid of the entire docstring when the name of the functions and parameters
are obvious.

So if you ever need to introduce an interface in Python3, I highly suggest you use
annotations to describe the types of your arguments. Future you and users of
your interface will thank you for this.

## One last word

They are tools like [mypy](http://mypy-lang.org/) that go even further and use
annotations to provide gradual static typing for Python.

I never used any of them (yet), because for now I'm happy catching type errors
through linters and automatic tests, but if you have, please let me know!
