---
slug: how-i-lint
date: 2017-04-14T10:34:55.624890+00:00
draft: false
title: How I Lint My Python
tags: ["python", "vim"]
---

This is a short post describing how I lint my Python code. You'll see it's
a bit more than just installing some plug-ins in a IDE, instead it's a little
bit of scripting code.

<!--more-->

# What is linting?

Linting is the process of running a program that will analyze code for potential
errors.

You give it the path of your sources, and it outputs a list of messages.

# What's wrong with linting in an IDE?

Nothing! It's just that I prefer having the liberty to run the linters only when
I need them, and that having scripts is useful when you do continuous
integration.

# The linters I use

I use several of them, because they all complement each other nicely:

* `pycodestyle` for checking the style
* `pyflakes` for fast static analysis.
* `mccabe` to find code that is too complex and needs refactoring
* `pylint` for everything else.

# Finding the sources

The first thing you need to take care of is getting the list of files you want
to run your linters on.

It's not that easy because every linter has its own syntax, and there are some
parts of your code you _know_ you don't want linters  to run on.

For this, I write a bit of Python code, using `path.py`

```python
# in ci/utils.py

import path


def collect_sources(ignore_func):
    top_path = path.Path(".")
    for py_path in top_path.walkfiles("*.py"):
        py_path = py_path.normpath()  # get rid of the leading '.'
        if not ignore_func(py_path):
            yield py_path
```

The `collect_sources` function takes a callback as parameter,
which allows to ignore some of the files.

# Running pyflakes

```python
# in ci/run-pyflakes

import subprocess

from .utils import collect_sources

def ignore(p):
    """ Ignore hidden and test files """
    parts = p.splitall()
    if any(x.startswith(".") for x in parts):
        return True
    if 'test' in parts:
        return True
    return False


def run_pyflakes():
    cmd = ["pyflakes"]
    cmd.extend(collect_sources(ignore_func=ignore)
    return subprocess.call(cmd)


if __name__ == "__main__":
    rc = run_pyflakes()
    sys.exit(rc)
```

Here, I have to make sure `pyflakes` does not run on test files, because it sometimes
get confused by `pytest` fixtures magic.

# Running mccabe

For `mccabe` it's the same thing, except I had to write a little bit of code
to make sure I get a nice, machine-readable output:

```python
# In ci/run-mccabe.py

import ast
import mccabe


def process(py_source, max_complexity):
    code = py_source.text()
    tree = compile(code, py_source, "exec", ast.PyCF_ONLY_AST)
    visitor = mccabe.PathGraphingAstVisitor()
    visitor.preorder(tree, visitor)
    for graph in visitor.graphs.values():
        if graph.complexity() > max_complexity:
            text = "{}:{}:{} {} {}"
            return text.format(py_source, graph.lineno, graph.column, graph.entity,
                               graph.complexity())


def main():
    max_complexity = int(sys.argv[1])
    ok = True
    for py_source in yield_sources():
        error = process(py_source, max_complexity)
        if error:
            ok = False
            print(error)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
        main()
```

Note how the complexity threshold is passed directly as a command line argument.

It will allow you to fine-tune this parameter. For me, 10 is a good value, but
depending on your code base, you may need to lower or increase it.

# Running pylint

I've already written [a post about pylint](
{{< ref "post/2016-07-23-some-pylint-tips.md" >}}). In a nutshell, you should
carefully edit your `.pylintrc` file and make sure to collect your Python
packages correctly.

# Putting it all together

Just a simple bash script:

```bash
#!/bin/bash -xe

pycodestyle .
python bin/run-pyflakes.py
python bin/run-mccabe.py 10
pylint mymodule
```

You may wonder why I don't use tools such as `flake8` or `prospector`.

Well, `flake8` does not run `pylint`.

`prospector` on the other hand is nice but forces you to use specific versions
of all the other linters, and is not so easy to configure. Plus, I discovered
its existence only *after* writing the script :)

Also, I've stopped tyring to use tools such as `tox` or `invoke`. I don't need
to test for several Python versions, (that's the main reason to use `tox`),
and the additional complexity of specifying commands in `invoke` is just not worth it.

Finally, even on Windows I'm mostly running commands in `git-bash`, so I don't
mind the script being written in bash.

# Running the linters from vim/neovim

Just use:

```vim
set makeprg=ci/lint.sh
```

And then run `:make`.

All the problems will appear in the quickfix window.

As I said at the beginning, I don't like my linters running while I'm editing,
so I'm OK with the linters being run synchronously, but I you need, there's
problably a plugin you can use for this.

Cheers!
