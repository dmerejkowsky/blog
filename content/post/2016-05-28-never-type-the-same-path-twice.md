+++
slug = "never-type-the-same-path-twice"
date = "2016-05-28T17:29:24+02:00"
draft = false
title = "Never Type the Same Path Twice"
tags = ["vim"]
+++

This is a follow-up of my [previous post]({{< ref "post/2016-04-30-vim-cwd-and-neovim.md"
>}}) on Vim and `cwd`, so I suggest you go read it first.

If you've read the previous post carefully, you may have noticed that
the ultimate goal of all the shortcuts I've described (`<leader>cd`),
(`<leader>ew`) or the way I care about the working directory of each vim tab,
always boils done to one thing:
**do not type the same path twice**

Here are a few more tricks I use on top of the other vim settings I've
previously described.

<!--more-->

## `vim --remote`

This is useful when you have two terminals open.

Here's an example:

![vim remote example](/pics/vim-remote.png)

In this case, the working directory on the left is correct, but the
`vim` instance running on the right was started from `$HOME`

Let's assume you want to edit `~/src/dmerej/blog/content/post/hello.md`.

You don't want to type `~/src/dmerej/blog/content/post/` again.

A solution is to use `vim --remote hello.md` from the terminal on the left.

{{< note >}}
This only works if the first `vim` instance was started using the `--servername`
option
{{< /note >}}

### Neovim

`Neovim` folks removed the `--remote` and `--servername` options.

The idea is that you should use the new RPC interface instead.

You can use a [nvr](https://github.com/mhinz/neovim-remote) or your own
solution.

Personally, I have something like this:

```python
# in vim_wrapper.py

SOCKET_PATH="/tmp/neovim"

def remote_nvim(filename):
    nvim = neovim.attach("socket", path=SOCKET_PATH)
    nvim.command(":e %s" % filename)

def main_nvim():
    env = os.environ.copy()
    env["NVIM_LISTEN_ADDRESS"] = SOCKET_PATH
    rc = subprocess.call(["nvim"], env=env)

def main():
    if "--remote" in sys.argv:
        remote_nvim()
    else:
        main_nvim()
```

In a nutshell:

* If `vim_wrapper.py` is called without a `--remote` argument,
  I make sure `Neovim` is always listening
  to the same socket (`/tmp/neovim`)

* Otherwise I use the `neovim` Python client API to attach
  to a running `Neovim` instance and open the file there.

(More about `vim_wrapper.py` later ...)

## Open recent files

I use the [Ctrl-P](https://github.com/kien/ctrlp.vim) plugin.

It has a "Most Recent Used" mode that I find very convenient.

This means that most of the time, I start `vim` from anywhere,
then run `<leader>p` (which is bound to `CtrlPMRUFiles`), and
only then do I set the working directory. (with `<leader>cd`,
remember?)

## Changing directory after Vim exits

Often, when I'm done editing, I want to run some `git` commands.
(Typically, `git push`)

So I use this trick to change the working directory of the calling
terminal.

First, I use an auto command to write the working dir in
an hard-coded file (`/tmp/nvim-cwd`)

```vim
" Write cwd when leaving
function! WriteCWD()
  call writefile([getcwd()], "/tmp/nvim-cwd")
endfunction

autocmd VimLeave * silent call WriteCWD()
```

Then I define a zsh function to call the `vim_wrapper.py` script
and change the working directory accordingly:

```bash
# Change working dir when Vim exits
function vim() {
  vim_wrapper.py $*
  cd $(cat /tmp/nvim-cwd)
}
```

## `z`: or the `cd` that learns

But sometimes I first want to change working directory *before* running
`vim`. (Typically, to run `git pull`)

To do so I use [z](https://github.com/rupa/z).

This tool installs a `zsh` hook and store every working directory in
a "database".

Then you can just type a small part of the directory you want to go to,
and it will use a "frecency" algorithm to get you there.

See the [README](https://github.com/rupa/z/blob/master/README) for more
information.

## Opening files from error messages

Often, in error messages you get something like:

<pre>
/path/to/foo.cpp:42: 'spam' was not declared in this scope
</pre>

There's the filename, followed by a colon (`:`), followed by a line number.

Of course, you want to open the file in `vim` to fix  it.

You can try to carefully select only the filename without the
`:42` part, or after having copy/pasted the full word, removing
the extra characters using `backspace`.

And then you remember `42` and type `42G` (or `:42`)
to go to the correct line.

Personally, I do this in the `vim_wrapper.py` script:

It tries to see if there are column in filenames, and
then starts vim with the correct `+` option:

```python
def parse_filespecs_for_cmdline(filespec):
    if ":" in filespec:
        parts = filespec.split(":")
        line = parts[1]
        filename = parts[0]
        return ["+%s" % line, filename]
```

Or, when used with the `--remote` option, opens a new tab
and the move the cursor to the correct location:

```python
def parse_filespecs_for_remote(filespecs):
    res = list()
    for filespec in filespecs:
        parts = filespec.split(":")
        parts += ["1"] * (3 - len(parts))
        parts[0] = os.path.abspath(parts[0])
        for i in (1, 2):
            try:
                parts[i] = int(parts[i])
            except ValueError:
                sys.exit("Failed to parse %s" % filespec)
        res.append(parts)
    return res

def remote_nvim(filespecs):
    nvim = neovim.attach("socket", path=SOCKET_PATH)
    to_open = parse_filespecs_for_remote(filespecs)
    nvim.command(":tabnew")
    for fullpath, line, column in to_open:
        nvim.command(":e %s" % fullpath)
        nvim.feedkeys("%iG" % line)
        nvim.feedkeys("%i|" % column)

```

# Conclusion

That's all folks :) Hope you liked it.

You can see the `vim_wrapper` script in my
[dotfiles repo on github](https://github.com/dmerejkowsky/dotfiles)
