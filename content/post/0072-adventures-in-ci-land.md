---
authors: [dmerej]
slug: adventures-in-ci-land
date: 2018-06-04T18:21:30.504290+00:00
draft: false
title: "Adventures in CI land"
tags: [ci, python]
---

Today  at work I wrote a CI script to test a react application, and it turned out to be a bit trickier than expected.

Let's try and reproduce the interesting issues I had and how I solved them.

# Setting the stage

Here's what you are going to need if you want to try and reproduce what I did.

* Node.js, yarn
* Python3 and `pipenv`
* The `chromedriver` binary.

Let's start by creating a simple React application:

```bash
$ yarn global add create-react-app
$ create-react-app hello
$ cd hello
$ yarn
```

We now have a beautiful React application running in our favorite browser.

Let's edit the `App.js` file to display `Hello, world` instead:

```javascript
import React, { Component } from 'react';

class App extends Component {
  render() {
    return (
      <p>Hello, world!</p>
    );
  }
}

export default App;
```

# Adding some end-to-end tests

Let's use `pipenv` to create a virtualenv with what we need:

```
$ pipenv install pytest
$ pipenv install selenium
$ pipenv shell
```

Now let's add some end-to-end using selenium and pytest. [^1]


```python
# in test_hello.py
import selenium.webdriver


def test_home():
    driver = selenium.webdriver.Chrome()
    driver.get("http://127.0.0.1:3000")
    assert "Hello, world!" in driver.page_source
```

We can now run the tests with pytest as usual:


```
$ pytest
collected 1 item

test_hello.py .                            [100%]
1 passed in 4.77 seconds
```

OK, it works!

Now let's imagine you have a team of people working on the application, and you would like these tests to run any time someone creates a merge request on this repo.

This is known as *continuous integration* (CI for short) and, trust me on this, it works a lot better than telling your teammates to remember to run the tests before submitting their changes for review!

# Writing the CI script

We use `GitLab` at work and are big fan of its CI features.

If you don't know GitLab CI at all, here's how it works:

* You install and configure the `gitlab-runner` program on some machines (called *runners*)
* Then you write a `.gitlab-ci.yml` file that contains the job description.

At my job we prefer to keep the `.gitlab-ci.yml` simple, and keep the code of the CI scripts separate, like this:

(note how we use `python3 -m pipenv` instead of just `pipenv`. This is to make sure `pipenv` runs with the expected version of Python)

```yaml
# in .gitlab-ci.yml

stages:
 - check

check:
  stage: check
  script:
    - python3 -m pipenv install
    - python3 -m pipenv run python ci.py
```


```python
# in ci.py

def main():
    # Call yarn here


if __name__ == "__main__":
    main()

```

We do this because it makes it easy to reproduce build failures found during CI locally. Any developer on the team can run `python ci/ci.py` on their machine directly instead of trying to copy/paste code from the yaml file.


# Going headless

Right now, the selenium tests use a full-fledged Chrome to run the tests. This is nice for the developers, but not so nice on a GitLab runner.

It would be much better to have those running in a headless Chrome instead, i.e without any GUI.

Let's fix that by adding a `--headless` option:

```python
# in conftest.py

import pytest

def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true")


@pytest.fixture
def headless(request):
    return request.config.getoption("--headless")
```

{{< highlight python "hl_lines=3 6-8" >}}
# in test_hello.py

from selenium.webdriver.chrome.options import Options as ChromeOptions

def test_home(headless):
    options = ChromeOptions()
    options.headless = headless
    driver = selenium.webdriver.Chrome(chrome_options=options)
    ...
{{</ highlight >}}


Now if we run `pytest` with the `--headless` option, the `headless` parameter of the `test_home` function will be set to `True` by pytest.
That's how pytest *fixtures* work.

Anyway, we can now check this is working by running:

```bash
$ pytest --headless
```

# Writing the CI script


So now we are faced with a new challenge: we need to run `yarn start` *before* running `pytest`, and kill the React script when the selenium tests have finished.

A nice way to do this in Python is to use the `with` statement, so let's do that:

```python

class BackgroundProcess:
    """ Run `yarn start` in the background. Ensure the yarn process
    is killed when exiting the `with` block

    """
    def __init__(self):
        self.process = None

    def __enter__(self):
        self.process = subprocess.Popen(["yarn", "start"])

    def __exit__(self, type, value, tb):
        self.process.terminate()

def main():
    with BackgroundProcess("yarn", "start"):
        subprocess.run(["pytest", "--headless"], check=True)


if __name__ == "__main__":
    main()
```

The `__enter__` method will be called right before the contents of the `with` block, so before `pytest` starts.
Then the `__exit__` method will be called after `pytest` is done, *even if an exception occurred*, passing data about the exception as arguments to the `__exit__()` method. Since we don't want do to anything other than re-raise if this happens, we just ignore them.

Anyway, this is much more readable than using `try/except/finally`, don't you think?

We still need a tiny fix: by default, `yarn start` will open a new tab on our browser. This was great while we were working on the JavaScript code, but here we are working on the CI script, so we'd prefer to disable this behavior.

Fortunately, all we have to do is to set the `BROWSER` environment variable to `NONE`:

```python
class BackgroundProcess:
    ...

    def __enter__(self):
        env = os.environ.copy()
        env["BROWSER"] = "NONE"
        self.process = subprocess.Popen(self.cmd, env=env)
```

Note: you may wonder why we did not just set the `BROWSER` environment variable directly in the `.gitlab-ci.yml` file. This would have worked, but here we create a special *copy* of the current environment variables, and we set the `BROWSER` environment variable *just for the `yarn` process*. Why?

Well, if you think of environment variables as nasty global variables (and you should: the environment of a process is just a big mutable shared state), it makes sense to limit their scope this way.

Anyway, back to the main topic:

# The bug

{{< note >}}
The rest of the article assumes you are using Linux. Things may work a bit differently (or not at all) on other operating systems.
{{</ note >}}

Let's see if the CI script works.

```
$ python ci.py
yarn run v1.7.0
$ react-scripts start
Starting the development server...
...
1 passed in 4.77 seconds
```

Let's run it a second time just to check that the `yarn` process was indeed killed:

```
$ python ci.py
? Something is already running on port 3000. Probably:
  hello (pid 16508)

Would you like to run the app on another port instead? (Y/n)
```

Uh-oh.

Let's run `pgrep` to check that the `yarn` process is dead:

```
$ pgrep yarn
[err 1]
```

The yarn process *is* dead. What gives ?

If we take a look at the `.terminate()` implementation, here's what we find:

```python
# in /usr/lib/python3.6/subprocess.py

class Popen:

      def send_signal(self, sig):
          """Send a signal to the process."""
          # Skip signalling a process that we know has already died.
          if self.returncode is None:
              os.kill(self.pid, sig)

      def terminate(self):
          """Terminate the process with SIGTERM
          """
          self.send_signal(signal.SIGTERM)
```

So, `terminate()` just sends the `SIGTERM` signal using the process ID (`pid`). The bug's not there.


# The naked truth

The truth is we've just created an orphan (we're monsters!)

When we ran `yarn start`, the `yarn` process looked at a section named `start` in the `package.json` and found something like this:

```javascript
{
...
  "scripts": {
    "start": "react-scripts start",
    ...
  }
}

```

It then created a *child* process, namely `react-scripts start`, with a *different PID*.

So when we killed the parent process, the `node` process became an orphan since its parent was dead (poor little process).

On Linux at least, all orphans process get automatically re-attached to the first ever process that was created since the machine booted. (`systemd` on my machine). This process always has a PID equal to&nbsp;1 and is often referred to as `init`.

We can check that by running `pstree`:

```
$ pstree
systemd─┬                               <- PID 1
...
        ├─node──                        <- our poor orphan
...
        ├─plasmashell─┬
                      ├─konsole─┬─zsh─  <- our shell
```


So how do we make sure the `node` child process gets killed too?

There are some fancy ways to fix these kind of problems (we could use `cgroups` for instance), but we can do it just with the Python stdlib.

Turns out we can use the `start_new_session` argument in the `subprocess.Popen()` call. This will create a *session* and attach the `yarn` process (and all its children) to it.

Then we can send the `SIGTERM` signal to the PID of the parent, and all the processes in the session will receive it:


{{< highlight python "hl_lines=1-2 6 9" >}}
import os
import signal

def __enter__(self):
  ...
  self.process = subprocess.Popen(self.cmd, start_new_session=True)

def __exit__(self):
    os.killpg(self.process.pid, signal.SIGTERM)
{{</ highlight >}}

Now if we re-run our script, we can see that neither `yarn` or `node` remain alive when the CI script terminates:

```
$ python ci.py
$ pgrep yarn
[err 1]
$ pgrep node
[err 1]
```

That's all for today. Cheers!


[^1]: This is not the first time I've used those tools to write end-to-end tests for Web application. See [Porting to pytest]({{< ref "post/0059-porting-to-pytest-a-practical-example.md"  >}}) for instance.
