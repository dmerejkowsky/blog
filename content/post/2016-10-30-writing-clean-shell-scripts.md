---
slug: writing-clean-shell-scripts
date: 2016-10-30T16:04:30.528337+00:00
draft: false
title: Writing Clean Shell Scripts

---

I don't enjoy writing such code that much.

It's often used when all you want is automate a mundane task.
"I'll just copy/paste the commands I usually run, add a few `if`s and `for`s
and that will be enough"

Well, that's how many shell scripts come to existence I guess, but nonetheless
writing such scripts is not as easy as it sounds, and there are many pitfalls to avoid.

Here a few tips you may find useful.

<!--more-->

## Use Bash

Sometimes you'll come across a `.sh` script with a `/bin/sh` shebang.
(That is, a file that starts with `#!/bin/sh`)

I believe you should not do that, unless you know what you are doing.

If your script starts with `#!/bin/sh`, it's telling the operating system
that the script should be run with the `/bin/sh` binary.

POSIX says that `/bin/sh` should exist and point to a "POSIX compliant" shell.

But on debian, it's a symlink to `/bin/dash`, and on Arch Linux, it's a symlink
to `/usr/bin/bash`.

So if you use a `#!/bin/sh` shebang, be prepared to get weird errors when
switching distributions, _or_ prove yourself that the code you wrote is indeed "POSIX".

I find it much easier to just stick a `#/bin/bash` shebang and call it a
day.

_Update: It seems bash will still do The Right Thing (tm) if it detects
that argv[0] is /bin/sh_


## Enable nice options

Bash has a lot of "switches" you can activate with the `set` built-in.

(Type `set -o` to get a list of them)

Here are a few useful ones.

### `set -e`

(Or `set -o errexit` if <a href="{{< relref
"2016-04-23-dont-use-short-options.md" >}}">using long options</a>
better suits you)

Adding that at the top of the script will make sure errors will not be silently
ignored, which is nice.

Note if you _do_ want to allow a command to fail, you can simply use a `|| true`
to do the trick:

```bash
#!/bin/bash
set -o errexit

cd path/to/foo
command-that-may-fail || true
```

###  `set -u`

(Or `set -o nounset`)

You will get an error each time you use a "unbound" variable, that is a
variable that has no value yet.

```bash
set -o nounset

my_option="foo"

echo $my_optoin
```

```console
$ bash foo.sh
foo.sh: line 4: my_optoin: unbound variable
```

_Update: By the way, you should really use `printf '%s\n' "$my_option"`
instead to avoid problems if for instance `my_option` is `-e`_


### `shopt -s failglob`

Let's say you want to do something with all the markdown files (ending with
`.md`) in the current directory.

But sometimes there are no such files:

```bash
# Without `shopt -s failglob`
$ do_something *.md
# calls do_something with the literal '*.md' string

# With shopt -s failglob
$ do_something *.md
# fails with:
foo.sh: line 6: no match: *.md
```

## Avoid useless pipes

Very often you can get rid of a pipe if you use the correct syntax.

Here are some examples:

```bash
# bad
cat foo.txt | grep bar
# better
grep bar foo.txt

# bad
grep bar foo.txt | wc -l
# better
grep -c bar foo.txt

# you want to replace 'foo' by 'bar' in the
# value of $my_var:

# bad
my_new_var=$(echo $my_var | sed -e s/foo/bar/)
# better
my_nev_var=${my_var/foo/bar}
```

By the way, the last example is one of the many things you can do with Bash
variables. Here's a list of the
[parameter substitutions](http://www.tldp.org/LDP/abs/html/parameter-substitution.html)
you can use.

## Learn to use sub-shells

Let's say you want to run the `make` command in all the subdirectories of your
current working directory.

```text
proj_1
|_ Makefile
|_ proj_1.c
proj_2
|_ Makefile
|_ proj_1.c
```

You may start by writing:

```bash
for project in */; do
  cd ${project} && make
done
```

But that won't work. After `cd proj_1`, you must go back to the top directory
so that `cd proj_2` can work.

You *could* workaround that using `popd` and `pushd` that allow you to maintain
a "stack" of working directories, but there's an easier way:

```bash
for project in */; do
  (cd ${project} && make)
done
```

By using parentheses, you've created a "sub-shell" that won't interfere with the
main script.

## Use static analysis

Yes, you can do this for bash scripts too :)

I like to use [shellcheck](https://www.shellcheck.net/) for this.

Here's a sample of what `shellcheck` can do:

```text
In foo.sh line 40:
find . -name "*.back" | xargs rm
^-- SC2038: Use -print0/-0 or -exec + to allow for non-alphanumeric filenames.

read name
^-- SC2162: read without -r will mangle backslashes.

$bin/foo bar.txt
^-- SC2086: Double quote to prevent globbing and word splitting.

my_cmd *
^-- SC2035: Use ./*glob* or -- *glob* so names with dashes won't become options.
```

The best thing about `shellcheck` is that each error message leads you to a
detailed page explaining the issue.


## Be careful with coreutils

The so-called `coreutils` (`cp`, `mv`, `ls`, ...) come with various flavours.
Basically, there's the "GNU" and the "BSD" flavors, so be careful to not use
things that only work in the "GNU" version.

This can happen when you switch from linux to OSX or vice-versa.

(for instance `cp foo.txt bar.txt --verbose` will _not_ work on OSX, you have
to put the option `--verbose` before the arguments)


## Alternatives to shell scripts

Actually, I'd highly recommend using a high level langage for this.

For instance, with Python, [path.py](https://pypi.python.org/pypi/path.py) and
[sh](https://amoffat.github.io/sh/) you can write
code that "feels" like shell script but is not:

```bash
# In Bash:
for project in */ ; do
  (
    cd "${project}"
    git clean --force
    git reset --hard
    make
  )
done
```

```python
# In Python:
import path
import sh

for project in path.Path(".").dirs():
    with project:
        sh.git.clean(force=True)
        sh.git.reset(hard=True)
        sh.make()
```

Note that by default `sh` swallows the output when the command is successful,
but displays a nice error message when something goes wrong, which is usually
what you want. If you still want to display the output of the command, you can
use `print(sh.make())` or something similar.
