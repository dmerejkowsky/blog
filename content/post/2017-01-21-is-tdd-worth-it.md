---
slug: is-tdd-worth-it
date: 2017-01-21T12:52:53.361088+00:00
draft: true
tags: ["testing"]
title: Is TDD Worth It?
---

Well, here is a good question!
Here's what I have to say:

1. I don't know
2. It depends

Those are, by the way, two very valid answers you can give
to any question. It's OK to not have a universal answer to
everything ;)

Still, I guess you want me to elaborate a tad more, so here goes ...

<!--more-->

## My testing story

I'll start by describing my own experience with testing in general, and TDD more
specifically. Hopefully it will help you understand how I came to the above
answer. It's a long story, so if you prefer, you can jump directly to the
conclusion.

### Shipping software

The story begins during my first "real" job.
I was working in a team that had already written quite a few lines of
`C++` code. We were using `CMake` and had several `git` repositories.

So I wrote a command-line tool in Python named `toc`[^1] that would:

* Allow developers to fetch all the git repositories into a common "workspace"
* Run `CMake` with the correct options to configure and build all the
  projects.

The idea was to abstract away the nasty details of cross-platform `C++`
compilation, so that developers could concentrate on how implement the
algorithms and features they were thinking about, without having to care
on such low-level details such as the build system.

The tool quickly became widely used by members of my team, because the
command line API was nice and easy to remember.

```console
$ cd workspace
$ toc configure
$ toc build
$ toc install /path/to/dest
```

It also became to be used on the buildfarm, both for continuous integration
and release scripts.

So I had to add new features to the tools, but without breaking the workflow of
my fellow developers.

I decided to advise my co-workers to _not_ use the latest commit on the `master`
branch, and told them they should instead use the "latest stable release" [^2].

Testing was complicated: the code base was already quite large, and the safest
way to make sure I did not break anything was to re-compile everything from
scratch (that alone took something like 15 minutes), and then perform a few basic
checks such as:

* Did the newly-compiled binaries run? [^3]
* Was incremental build working?

### Making testing easier

My first idea was to write a bunch a "example" code.

Instead of having to compile hundreds of source code files spread across
several projects, I could use just two projects with very few source code in
them.

So I wrote code for two new projects, like so:


```text
test
  world
    CMakeLists.txt
    world.h
    world.cpp
  hello
    CMakeLists.txt
    main.cpp
```

The `world` project contained source code for a shared library,
(`libworld.so`), and the `hello` project contained source code for an
executable (`hello-bin`) that was using `libworld.so`.

Compiling `world` and `hello` from scratch just took a few seconds, so testing
manually was easy.

But I was not very good at testing manually. Quite often I forgot to test some
corner cases, and so many bugs were introduced without me noticing.

So I decided to start writing automated tests.


### First tests

![I find your lack of tests disturbing](/pics/lack_of_tests.jpg)

The tests looked like:

```python
class ConfigureTestCase(TocTestCase):

    def setUp(self):
        pass

    def test_configure(self):
        self.run(["toc", "configure", "hello"])

    def test_build(self):
        # We need to configure before we can build:
        self.run(["toc", "configure", "hello"])
        self.run(["toc", "build", "hello"])

    def test_install(self):
        # We need to configure and build before we can install:
        self.run(["toc", "configure", "hello"])
        self.run(["toc", "build", "hello"])
        self.run(["toc", "install", "hello", self.test_dest])
        # do something with self.test_dest

    def tearDown(self):
        # Clean the build directories:
        super().clean_build()
        # Clean the destination directory for install testing:
        if os.path.exists(self.test_dest):
            shutil.rmtree(self.test_dest)
```


Few things to note here:

* No asserts
* The code to run the `toc` commands and cleaning the build directories
  is in a `TocTestCase` base class
* If something goes wrong, it's hard to know exactly why because we don't
  know which build directories are "fresh"
* It's not clear where the installed files go ...
* Tests are slow because `hello` and `world` get compiled a lot of times.

At the time, that's all the tests I had.

That meant I could do refactoring without fearing regressions to much, but
I still had to run *the entire test suite* to be a little more confident about
any change I just made.

I also started measuring test coverage [^4] and was unhappy with the results.
(60% if I recall correctly)

I also noticed that even though I was very careful, every release I made had
some serious regressions, and so members of my team started to get reluctant to
the idea of upgrading.

Code was clearly becoming cleaner, but this was not a good enough reason for them
to upgrade.

### The Light At The End of the Tunnel

![A light at the end of a tunnel](/pics/light-at-the-end-of-a-tunnel.jpg)

The decision to try TDD came from several sources, I'm not sure which was the
decisive one at moment, but here are two of them:

* [Robert Martin: What Killed Smalltalk Could Kill Ruby, Too](
  https://www.youtube.com/watch?v=YX3iRjKj7C0)
* [Destroy All Software](https://www.destroyallsoftware.com/screencasts):
  "classic" seasons 1 to 5.
* [Boundaries](https://destroyallsoftware-talks.s3.amazonaws.com/boundaries.mp4), a talk
  by the same previous guy.

So there, I started using TDD for all the new developments, and I kept doing
that for several years.

The tool became known as `qibuild`, coverage went up, tests became more reliable
and useful [^5], regressions became more and more uncommon, adding new features
became simpler and easier, and overall everyone was happy with the tool.

For the curious, here what the tests looked like: [^6]

```python
def test_running_after_install(qibuild_action, tmpdir):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("install", "hello", tmpdir)

    hello = qibuild.find.find_bin(tmpdir, "hello")
    subprocess.run([hello])
```

### Turning into a TDD zealot

So, now I had finally solved that [xkcd puzzle](https://xkcd.com/844/): [^7]

![Good Code](/pics/xkcd_good_code_tdd.png)

All I had to do was to write tests first, and everything would be OK!

But no-one around me believed me.

A few of them tried, but they gave up soon.

Many of them were working with "legacy" code and just making sure the _old_
tests still pass was challenging enough.

I tried to told them about the [classical beginners mistakes](
http://blog.cleancoder.com/uncle-bob/2016/03/19/GivingUpOnTDD.html) but it did
not work.

But I was right! I had seen the light! It did not matter if I did not manage to
convince anyone, I was right, and they were wrong.

### The expert beginner

I began realizing how little I knew about testing thanks to this very blog.

You can read more about this in ["My Thoughts on: 'Why Most Unit Testing is Waste'"](
{{< ref "post/2016-06-04-my-thoughts-on-why-most-unit-testing-is-waste.md" >}}).

It was then I understood that maybe things were not that simple.

I wrote two more articles to remember myself that my thoughts on testing were not
completely black and white: [^8]

* [Is Line Coverage Meaningless?](
{{< ref "post/2016-06-18-is-line-coverage-meaningless.md" >}})
* [When TDD Fails](
{{< ref "post/2016-07-02-when-tdd-fails.md" >}})


### Realizing the truth

![There is no spoon](/pics/there-is-no-spoon.jpg)

This happened after I took a new job in an other company.

People there were ready to try, and I was lucky enough to be there
when two new projects started.

* One of them was some `C++` code to read and write large encrypted files.
* The other was a small piece of server written in `Go`.

Surely this time, people willing to try would have no excuse (no legacy code
this time!), and I even gave a talk to the whole team about TDD [^9]

But nope, it did not go as I expected:

* For the `C++` part, they used TDD until they started working on a small
  binary, that would crypt and encrypt files from `stdin` to `stdout`.
  "We'll use the binary during QA, surely we don't need to use TDD just
  to _write_ source code of the binary.", they say. "Plus, we already have tests
  where we mock the `Encryptor` class, no need to write and run the same tests
  with the 'real' encryptor class, bugs will be caught during QA anyway".

* And in `Go`, they wrote a few tests, but not that much, and many issues were
  caught by the compiler and the various linters they used anyway.[^10]

Maybe TDD was working for me just because:

* It suits the way my brain work. I have a hard time doing several tasks at
  once, and the whole idea of the 'red', 'green', 'refactor' cycle helps me
  focusing on just the right stuff at the right time.
* I suck at doing tests manually.
* I produce a lot of typos.
* I used a language where tests are _required_ to find problems. (The type
  system and the linters can only catch so much when you're using a
  "dynamic" language such as Python)
* I had a very good test framework, and writing clean test code was easy after
  the 3rd refactoring or so :)


### Applying TDD for a web application

One day, I wondered how hard it would be to implement a wiki from scratch.

The basic stuff seemed easy enough:

* The server known how to map the `/foo` URL and a `foo.html` file written on
  disk.
* When a user visits `/foo/edit`, he gets a form where he can type some
  Markdown code.
* Then, when he its the `submit` button, both `foo.md` and `foo.html` are
  generated.

#### Compiling


I decided to write the server in `Go`.

This was new to me, because it was the first time I was working with a language
with such a short compilation time.

I found myself forgetting to type `go build` before restarting the server, so
I wrote this short script:

```python
#dev.py

print(":: Starting loop")
print("> Will stop as soon as the build fails")
print("> To restart the server, press CTRL-C")

while True:
    cmd = ["go", "build", "server.go"]
    subprocess.check_call(cmd)
    try:
        cmd = ["./server"]
        subprocess.check_call(cmd)
    except KeyboardInterrupt:
        pass
```

Here's how the script works, assuming the `dev.py` script is running
and you are in a state where the server is running with the latest version of
the source code.

* You write some `Go` code
* You press `CTRL-C`:
  * If the code compiles, the server is restarted with the latest changes
  * If not, the script crashes, and you have to fix the build before
    re-running it.

Most of the time (especially when you get better at mastering the `Go`
language), you get the new version of code running very shortly after
saving the `.go` source file you were working on. [^11]

#### Testing

After a while, I started having the server generating `HTML` forms, and I
found myself filling the same form and hitting the `submit` button over and
over again.

So I started automating, using `py.test` and [selenium](http://www.seleniumhq.org/)

First, I wrote a fixture so that the server source code will always get built
before running:

```python
@pytest.fixture(autouse=True, scope="session")
def build_and_run():
    subprocess.check_call(["go", "build"])
    process = subprocess.Popen(["./server"])
    yield process
    process.kill()
```

Then I wrote my own `browser` fixture, using the "facade" design pattern to
hide the `selenium` API:


```python

class Browser():
    def __init__(self):
        self._driver = webdriver.Chrome()

    def click_button(self, button_id):
        button = self._driver.find_element_by_id(button_id)
        button.click()

    def read(self, path):
        full_url = "http://localhost:1234/%s" % path
        self._driver.get(full_url)
        return self._driver.page_source
```

This allowed me to write things like this:

```python
def test_edit_foo(browser):
    browser.read("/foo/edit")
    browser.fill_text("input-area", "Hello, world")
    browser.click_button("submit-button")
    assert "Hello, world" in browser.read("/foo")
```


That turned out to be a very nice experience.

I could:

* Insert a breakpoint using `pdb`
* Start the test I wanted with `pytest -k edit_foo`
* And when the code was paused, interact with the browser and experiment in
  Python's REPL to write the rest of the tests and the assertions, without first
  learning the entire `selenium` API by heart.

Then again, the feedback look was very short. I could edit the `HTML` to add
the proper `id` attribute, and then re-run the tests to check if the generated
HTML looked good in a web browser.

So, was I writing tests before or after? And did it matter?

### Writing Software

Around the same time, I watch *Writing Software*, a talk David Heinemeier Hansson
gave in RailsConf 2014 Keynote.

You can watch the talk on [youtube](https://youtu.be/9LfmrkyP81M).

In it, David talks about TDD, but it's only a small fraction of his talk, and I
highly recommend you listen to the whole talk and not focus on the most
controversial parts.

Anyway, the talk gave me a lot to think about.

### The 'what', the 'how' and the 'why'


[^1]: "Toc means Obvious Compilation". Yes, it was a silly name.
[^2]: That's where I realized how important [changelogs]({{< ref "post/2016-10-01-thoughts-on-changelogs.md" >}}) were.
[^3]: It's not that obvious when your binaries are built for Linux, macOS and Windows, and there are `.so`, `.dylib` and `.dll` files involved.
[^4]: At the time, I thought it was a good idea to measure test coverage. <br /> I've [changed my mind]({{< ref "post/2016-06-18-is-line-coverage-meaningless.md" >}}) since
[^5]: By that I mean that I started having just a few tests failures that pointed me directly to the bug I just introduced.
[^6]: Using [pytest]({{< ref "post/2016-04-16-pytest-rocks.md" >}}) of course!
[^7]: [Randall](https://en.wikipedia.org/wiki/Randall_Munroe), if you see this, I'm so sorry.
[^8]: Fifty shades of testing?
[^9]: I used stuff I learned from [Uncle Bob's videos on the subject](https://cleancoders.com/videos/clean-code/advanced-tdd)
[^10]: We use [gometalinter](https://github.com/alecthomas/gometalinter) by the way.
[^11]: You may wonder how I managed to write the contents of the `dev.py` file itself. Short answer: I used `CTRL-\`, which makes Python exit with a core dump and effectively exit the `while True` loop even though the code compiles.
