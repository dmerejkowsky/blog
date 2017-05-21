---
slug: rewriting-z-from-scratch
date: 2017-05-21T12:54:02.249830+00:00
draft: false
title: Rewriting z from scratch
tags: ['python', 'vim', 'zsh']
---

[z](https://github.com/rupa/z) is a tool that will remember all the directories
you are visiting when using your terminal, and then make it possible to jump
around those directories quickly.

Let's try and rewrite this functionality from scratch, maybe we'll learn a few
things this way.

<!--more-->

# Motivation

I started using `z` about one year ago.

It worked fine except for one thing.

Let's say I have two directories matching `spam`, `/path/to/spam-egss`, and
`/other/path/to/eggs-with-spam`.

`z` will compute a score for each directory that depends on how often and how
recently it was accessed.

So, in theory:

> a  directory that has low ranking but has been  accessed
> recently will  **quickly**  have  higher rank than a directory accessed frequently a
> long time ago. (excerpt of `z`'s README, emphasis is mine)

But in practice, if you start working from `spam-eggs` to `eggs-with-spam`
you will get the wrong answer for `z spam`  a few times, ("quickly" does not
means "instantly")

Also, *because* the algorithm uses the date of access, you cannot
(easily) predict which directory it will choose.

# Step one: choose a database format

`z` uses a database that looks like this

```text
/other/path/to/eggs-with-spam|24|1495372880
/path/to/spam-eggs|4|1495372491
...
```

There's the path, the number of times it was accessed and the timestamp of last
visit.

We'll use `json`, and since we want an algorithm that does not
depend of the time, we'll only store the number of accesses:

```javascript
{
  "/other/path/to/eggs-with-spam": 24,
  "/path/to/spam-eggs": 4,
  ...
}
```

Why `json`? Because it's quite easy to read and write (including pretty print)
in any language, while still being editable by humans.

It still is possible to add new data should we need to.

# Step two: decide how to handle non-existing directories

Let's say you work in `/tmp/foo`, and no other directory is called `foo`.
You also create the directories `/tmp/foo/src` and `/tmp/foo/include`.

With `z`, once the three paths, `/tmp/foo` , `/tmp/foo/src/` and
`/tmp/foo/include` are stored in the database, they will stay there for ever.

This means that if you remove `/tmp/foo`, `z foo` will still try to go into the
non-existing directory. But, if you re-create `/tmp/foo` later on, `z foo` will
work again.

In our rewrite, we'll deal with this situation an other way:

* One, if we can't `cd` to a directory, we'll remove it from the database
  immediately
* Two, we'll make it possible to explicitly "purge" the database: in our
  example, that means removing all three paths in one step. To do this,
  we'll look at every path in the database and remove those which no longer
  exist.


# Step three: write a command line tool

I decided to name the tool `cwd-history`, and to use an command line syntax
looking like `git`, with several possible "verbs" for the various actions:

* `cwd-history list`: to display the paths in the correct order
* `cwd-history add PATH`: add a path to the database
* `cwd-history remove PATH`: to remove a path from the database
* `cwd-history edit`: to edit the json file directly (could become handy)
* `cwd-history clean`: to remove non-existing paths from the database

The code is [on github](
https://github.com/dmerejkowsky/dotfiles/blob/master/bin/cwd-history) if you
want to take a look.

Some notes:

```python
def get_db_path():
    zsh_share_path = os.path.expanduser("~/.local/share/zsh")
    os.makedirs(zsh_share_path, exist_ok=True)
```

* We honor XDG standard (in reality we should also check for the `XDG_DATA_HOME`
    environment variable, but this is better than polluting `$HOME`).

* We use the `exist_ok`[^1]  argument for `os.makedirs`, so that the command
  does not fail if the directory already exists.


```python
def add_to_db(path):
  path = os.path.realpath(path)
```

* We use `os.path.realpath` to make sure all the symlinks are resolved. This
  means that we won't have duplicated paths in our database.


```python
def clean_db():
    cleaned = 0
    entries = read_db()
    for path in list(entries.keys()):
        if not os.path.exists(path):
            cleaned += 1
            del entries[path]
    if cleaned:
        print("Cleaned", cleaned, "entries")
        write_db(entries)
    else:
        print("Nothing to do")
```

* We try to provide as many information as possible in just one line, by
  displaying either the number of directories that were cleaned, or that nothing
  was done. Listing all the paths that were removed would be too verbose, and if
  we did not display anything we would never be sure the command really
  worked.


```python
import operator

def list_db():
    entries = read_db()
    sorted_entries = sorted(entries.items(),
                            key=operator.itemgetter(1))
print("\n".join(x[0] for x in sorted_entries))
```

* We use `operator.itemgetter` as a shortcut to `lambda x: x[1]`
* Thus, we sort the paths by the number of times they were accessed.
* We only display the paths, each of them separated by one line. This will make
  the output of `cwd-history list` really easy to parse. (We could add a
  `--verbose` option to display the full database data for instance)


# Step four: hook into zsh

We want to call `cwd-history add $(cwd)` every time `zsh` changes the current
working directory.

This is done by writing a function and add it to a special array:

```bash
function register_cwd() {
  cwd-history add "$(pwd)"
}
typeset -gaU chpwd_functions
chpwd_functions+=register_cwd
```

* Note how `chpwd_functions` is a zsh array, so we have to use `typeset`. We
  call it with `-g` because `chpwd_functions` is a  *global value*, and `-U` to
  make sure the list contains no duplicates. I'm not sure what `-a` is for,
  sorry.


# Step five: filtering results

Instead of trying to guess the best result, we'll let the user choose by hooking
into `fzf`.

I already talked about `fzf` on a [previous article](
{{< ref "post/2017-05-17-fzf-for-the-win.md" >}}). The gist of it is that you
can pass any command as input to `fzf`, and let the user interactively select
one result from the list.

The implementation looks like this:

```bash
  cwd_list=$(cwd-history list)
  ret="$(echo $cwd_list| fzf --no-sort --tac --query=${1})"
  cd "${ret}"
  if [[ $? -ne 0 ]]; then
    cwd-history remove "${ret}"
  fi
```

Notes:

* We use `fzf` with `--query`, so that you can either type `z foo`, or just `z`,
  and only after type the `foo` pattern in `fzf`'s window

* Since the most likely answers are at the *bottom* of the `cwd-history list`
  command, we use `fzf` with the `--tac` option[^2]. We also need tell `fzf`
  to *not* sort the input beforehand.

* As explained earlier, we remove the path from the database if we can't
  `cd` into it. (This also covers the case where we are lacking permissions to
  visit the folder, by the way)

# Step six: from the shell to neovim and vice-versa

One last thing. Since I do most of my editing in neovim, I'm always looking for
ways to achieve similar behaviors in my shell and in my editor.

So let's see how we can transfer information about visited directories from one
tool to an other.

## From neovim to the shell

This is kind of a ugly hack.

First, I add a auto command to write neovim's current directly into a hard-coded
file in `/tmp/`:

```vim
" Write cwd when leaving
function! WriteCWD()
  call writefile([getcwd()], "/tmp/nvim-cwd")
endfunction

autocmd VimLeave * silent call WriteCWD()
```

And then, I wrap the call to `neovim` in a function that reads the content of
the file and then calls `cd`, but only if `neovim` exited successfully.

```bash
# Change working dir when Vim exits
function neovim_wrapper() {
  nvim $*
  if [[ $? -eq 0 ]]; then
    cd "$(cat /tmp/nvim-cwd 2>/dev/null || echo .)"
  fi
}
```

## From the shell to neovim

To go the other way, I just call `fzf#run()` from the
[fzf.vim](https://github.com/junegunn/fzf.vim) plugin with `cwd-history list` as
source and `:tcd` as sink:[^3]

```vim
function! ListWorkingDirs()
  call fzf#run({
        \ 'source': "cwd-history list",
        \ 'sink': "tcd"
        \})
endfunction

command! -nargs=0 ListWorkingDirs :call ListWorkingDirs()
nnoremap <leader>l :ListWorkingDirs<CR>
```

# Conclusion

And there you have it.

`z` is 458 lines of `zsh` code.

My re-implementation is 75 lignes of Python, 6 lines of `zsh`, and 8 lines of
`vimscript`.

It shares the database between the shell and the editor, it is never wrong, and
the database stays clean and editable by hand.

Not bad I think :)

PS: You can also use `z` directly with `fzf` with a few lines of code, as show
in [fzf wiki](https://github.com/junegunn/fzf/wiki/examples#integration-with-z)

[^1]: Here since Python 3.2
[^2]: It's `cat` in reverse, do you get it?
[^3]: `tcd` is a neovim-only feature. I already mentioned it in my [post about vim, cwd, and neovim]({{< ref "post/2016-04-30-vim-cwd-and-neovim.md" >}})
