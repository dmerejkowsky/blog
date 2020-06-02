---
authors: [dmerej]
slug: how-rust-made-me-a-better-python-programmer
date: 2020-05-01T12:19:25.455275+00:00
draft: true
title: "How Rust made me a better Python programmer"
tags: [python, rust]
summary: |
  The benefits of learning a radically different language
  than the one you are used to
---


# Getting out of my comfort zone

I've been written Python code for
almost 10 years now. It's the language I [fell in
love](https://medium.com/signal-v-noise/how-i-fell-in-love-with-a-programming-language-8933d5e749ed)
with.

One day, I decided to try Rust and it changed everything.

Why am I telling you about this?

Well, I've often read articles telling me to "try now things", or
"get out of my comfort zone", but  but those articles seldom gave *concrete
examples* of the benefits of learning a different programming language.

So, how did Rust made me a better Python programmer?

But it also had a direct effect on how I write Python code, so let's see a few examples.

# Types are good

First, it changed my mind about type systems and tests - I've already talked
about this in [I don't need types]({{< relref "0070-i-don-t-need-types.md"
>}}) and [giving mypy a go]({{< relref "./0071-giving-mypy-a-go.md" >}}),
so there's *that*.

I now use `mypy` with `--strict-optional` as often as I can, both for personal Python projects
and at work.

# More upfront design

When you are writing Rust, you first try to get the compiler to accept your code, and *then*
you have to satisfy the borrow checker.

That means that even though it's still possible to do TDD in Rust, your cycles are going to get a
bit longer, and that means you'll probably have to spend a bit more time in
upfront design.  For instance, you have to think about *data ownership*.

Let's see this in practice.

A while back, I was writing a command-line tool that would manage workspaces
and projects [^1].

Here's what my initial design looked like:

```python
class Workspace:
    """ A workspace contains a collection of named projects
    and a config

    """
    def __init__(root_path):
        self.root_path = root_path
        self.config = ...  # read config from root path
        self.projects = ....  # build a list of projects from the config


    def build_project(self, name):
        project_path = self.root_path / name
        return Project(name, path=project_path)

    def __repr__(self):
        project_list = ",".join(str(x) for x in self.projects)
        return f"<Workspace in {self.root_path} with projects {project_list}>"


class Project:
    """ A project has a name and a path

    """
    def __init__(self, name, *, path):
        self.name = name
        self.path = path

    def __repr__(self):
        return f"<Project {self.name} in {self.path}>"

```

So far so good.

Then I realized that some projects methods like `.build()` would need access to the workspace configuration, so that's
I changed:

```diff
    def build_project(self, name):
-       project_path = self.root_path / name
+       return Project(name, path=project_path, workspace=self)

class Project:
    """ A project has a name and a path

    """
-    def __init__(self, name, *, path):
+    def __init__(self, name, *, path, workspace):
        self.name = name
        self.path = path
        self.workspace = workspace

+    def build(self):
+        workspace_config = self.workspace.config
```

Easy, right? The config is inside the workspace, so let's pass a reference to the Workspace inside the Project
constructor and then use it's config in the `build()` method.

In case this is not obvious, here's one problem with this design : there's a cyclic reference : Workspace contains
projects that contains references to workspaces.

You can make the code blow up just by modifying Project's `__repr__` method:

```diff
class Project:
    ....

    def __repr__(self):
-        return f"<Project {self.name} in {self.path}>"
+        return f"<Project {self.name} inside {self.workspace}>"
```

```text
workspace = Workspace(Path("path/to/workspace"))
print(workspace)

  ....
  File "bad.py", line 46, in __repr__
    return f"<Project {self.name} inside {self.workspace}>"
  File "bad.py", line 31, in __repr__
    project_list = ",".join(repr(x) for x in self.projects)
  File "bad.py", line 31, in <genexpr>
    project_list = ",".join(repr(x) for x in self.projects)
RecursionError: maximum recursion depth exceeded while
getting the repr of an object
```

This is pretty bad because you often never write tests for the `__repr__` method - you use it only
when debugging something!

Writing Rust code made me *avoid* those kind of designs like the plague. You *can* create circular references but
it will be *much* easier to use plain, cheap, immutable references when you can.



Other exemple:

```python
class Workspace:
    def __init__(self, root_path: Path) -> None:
        local_manifest_path = root_path / ".tsrc" / "manifest"
        self.cfg_path = root_path / ".tsrc" / "config.yml"
        self.root_path = root_path
        self.local_manifest = LocalManifest(local_manifest_path)
        copy_cfg_path_if_needed(root_path)
        if not self.cfg_path.exists():
            raise WorkspaceNotConfigured(root_path)

        self.config = WorkspaceConfig.from_file(self.cfg_path)

```

This does too many things and is hard to test.

In Rust, I would have to consider making `Workspace::new` return a Result, or most likely

```rust
impl Workspace

 fn new(config: Config, manifest: manifest ) {

 }

 fn open(path: Path) -> Result<Self> {

 }

}
`


[^1]: The code is still on [GitHub](https://github.com/aldebaran/qibuild) and I feel kind of bad about it today :P



