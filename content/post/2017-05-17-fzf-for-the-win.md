---
slug: fzf-for-the-win
date: 2017-05-17T08:13:53.590982+00:00
draft: false
title: fzf for the win
---

Last month, I heard about [fzf](https://github.com/junegunn/fzf) for the first
time.

Today, it has become one of my favorite tools and I can no longer imagine
working on a computer without it installed.

Let me tell you how and why this happened.

<!--more-->

First, I'm going to describe quite a few different tools I was using,
both in my shell (zsh), and in my text editor (neovim).

Then, I'll show you how and why I replaced all this tools with `fzf` and
how it allowed me to have a better workflow.

# The dark times (before fzf)

![dark times](/pics/dark-times.jpg)

## Finding files in folders

Let's say I was trying to edit `FooManager.java`,
buried deep in a `src` folder.

My zsh history looked like this:

```bash
$ find -name foo
# Oups, forgot to put the dot
$ find . -name foo
# Oups, the file is not named 'foo' exactly, I need
# to add globs
$ find . -name *foo*
# Oups, I need to add quotes to prevent the shell
# from expanding the globs:
$ find . -name "*foo*"
# Oups, find is case-sensitive by default, so I need
# `-iname` instead of `-name`
$ find . -iname "*foo*"
src/main/java/com/example/foo/FooManager.java
# Now I can copy/paste the file path and
# edit the file in vim:
$ vi <shift-ctrl-v>
```

Phew! That's a *lot* of keystrokes for such a basic task!

## Browsing zsh history

### Going up and down

I would use `CTRL-N` and `CTRL-P` to navigate up and down the history.

For instance, if I've typed the following list of commands:

```bash
$ ls foo
$ ssh server1
$ ls bar
$ ssh server2
```

I could press `CTRL-P` three times to get `ssh server1`, and then it
`CTRL-N` to get `ls bar`.

### Using the arrow keys

There's an other trick I would use with zsh. Instead of listing all the commands
in chronological order, you can tell zsh to only display commands that start
with the same characters as your current line.

So I had something like this in my `~/.zshrc`:

```bash
bindkey '^[[A' history-beginning-search-backward
bindkey '^[[B' history-beginning-search-forward
```

And that meant I could do:

```bash
$ ssh <up key>
```

and then continue to press 'up' until I found the correct server. And if I went
too far, I could just press 'down'.

### Looking for a specific command

Sometimes I wanted to re-enter a command but I knew it was far down the history
list. Or, I remembered parts of the command, but not how it started.

So rather that hitting `CTRL-P` a bunch of times, I would use `CTRL-R` instead.

But using `CTRL-R` properly is not obvious. With my `zsh` config, I had to:

* Type `CTRL-R`
* Enter the pattern
* Make a typo
* Use `backspace` to fix the typo
* Hit `CTRL-R` many times
* Realize I went too far
* Carefully type `backspace` *once* to get to the previous match
* Press enter


Also, sometimes I would get the dreaded `failing bck-i-search` message which
often meant I had to start over.

## In neovim


### List buffers


In `neovim` you can use `:list` to list all the open buffers.

There are displayed like this:

```text
  1 %a + foo.txt
  3 #h   bar.txt
 10  a   baz.txt
```

Every buffer has a number. The columns between the number and the  name contains
info such as whether the buffer is active or hidden, if it's modified and so on.

The `#` sign mark the "alternate" buffer, that is, if you press `:b#` you'll go
back and forth from the alternate buffer to your current buffer.

You can switch to a buffer by using `:b<num>`, where `<num>` is the buffer
number.

And you can also use tab completion after `:b` to list all the buffer names
containing a certain pattern.

So, to open the buffer 'baz.txt', I would type:

```vim
:b bar
<tab>
" nope, I don't want bar.txt
<tab>
" ok, I got baz.txt
<enter>
```

This worked quite well, except sometimes I would get far too many matches,
and then I would spend quite a long time hitting `<tab>` to find the buffer I
wanted.

### Browsing old files

neovim keeps a list of all the file names you have edited.

You can display the list by using `:oldfiles`.

It looks like this:

```text
1: /home/dmerej/foo.txt
2: /home/dmerej/bar.txt
3: /home/dmerej/src/spam/eggs.py
-- More --
```

You have to press `enter` to see the rest of the list, and after
you've pressed `enter`, there is no way to go back.

You also can't search in the list.

And if you want to open one of the files, you have to use `:browse oldfiles`,
carefully remember its index, and when prompted, type the number and press
`<enter>`.

This is a bit tedious while all you want is a simple "Select From Most Recently Used" feature that almost every other text editor has :/

# Looking for patterns

![patterns](/pics/patterns.jpg)


This is a very general technique you can use when trying to improve your
workflow. Look for a pattern and then find one way to deal with it that you can
re-use everywhere.

So what's the pattern in all the tools I just showed you?

In every single case (from browsing the neovim buffers or trying to find something
in `zsh` history), we have a list (more or less sorted), and we want
to select *one and only one* element from the list.

We care deeply about interactivity: this means it should be easy to recover from
some mistakes, such as typing the letters in the pattern in the wrong order,
making typos, or not caring about case sensitivity.

Here's where `fzf` comes in.

# fzf for the win!

`fzf` does only one thing and it does it well. You are supposed to use it with a
shell pipe, like this:

```bash
$ some-source | fzf
```

Here `fzf` will use a few lines of text, displaying a list of elements,
returned by the `some-source` command. (By default the last `n` elements).

But while you are entering the pattern to filter the list of matches, it will
update the list in real time.

It will color the part of the lines that matches, and will allow you to enter
"fuzzy" patterns (allowing for typos and the like)

You can see it in action on [asciinema](https://asciinema.org/a/120929)

Note that:

* When used from `tmux`, you can use the `fzf-tmux` command instead, which will
  automatically display the list in a split panel.
* You can use symbols in the pattern to change how elements are filtered:
 * `'foo`: use a single quote to get an exact match
 * `^foo`: use a caret to select elements that start with `foo`
 * `foo$`: use a dollar to select elements that end with `foo`

* There's tons of info in `fzf` man page and in the [wiki](
  https://github.com/junegunn/fzf/wiki)

* `fzf` can also hook itself it the completion machinery of your shell. It
  pretty much "just works". See [the documentation](
  https://github.com/junegunn/fzf#fuzzy-completion-for-bash-and-zsh) for the
  details.

## Installation


```bash
$ git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
$ ~/.fzf/install
```

Note that `fzf` is written in Go which means:

* It's fast
* It has no dependencies
* It's cross-platform
* It can handle async stuff well

More precisely, it means you can start select things as soon as fzf starts,
*while fzf is still processing its input*.

## fzf out of the box

### zsh history

You can configure `fzf` so that it runs when you hit `CTRL-R`.

Personally, I also tell `fzf` to start when I hit the arrow key:

```text
bindkey '^[[A' fzf-history-widget
```

I'm so used to using arrow keys to navigate the zsh history that it makes sense
to just overwrite the behavior for this case.

Still, `fzf` is a bit overkill when all you want is to re-type exactly the
previous command, so I also configured `CTRL-N` and `CTRL-P` to do
"dumb" history navigation:

```text
bindkey '^P' up-line-or-history
bindkey '^N' down-line-or-history
```

### Replacing find

By default, when pressing `CTRL-T`, `fzf` will allow to select any file name in
the directory, recursively, and when you are done selecting it, it will insert
the path after your current line.

So for instance, you can use:

```bash
$ vim <ctrl-t>
# Start fzf
# Select Foo.java
# Press enter once, line becomes:
$ vim src/main/java/com/example/foo/Foo.java
# Press enter to edit the file
```

This is much more efficient than the "run find and copy/paste the results"
technique I was previously using :)

## fzf and neovim

By default, `fzf` installs a very light wrapper on top of the `fzf` executable.

Instead of the interactive list being displayed in a terminal, it will get
displayed in a special neovim buffer, but the rest of the usage (including the
keystrokes) will be the same as in the shell version.

I suggest you use [fzf.vim](https://github.com/junegunn/fzf.vim) which brings
you nice commands out of the box such as :

* `:History`, leveraging the `:oldfiles` command to edit old files
* `:Buffers`, to start editing a buffer in the current window
* `:Files`, to edit one of the files in the current directory and below


After installing the plug-in, all you have to do is to configure some mappings:

```vim
nnoremap <leader>p :History<CR>
nnoremap <leader>b :Buffers<CR>
nnoremap <leader>t :Files<CR>
```

`fzf.vim` also allow you to create your own command using a bit of
`vimscript`:

```vim
command! -nargs=0 MyCmd :call SelectSomething()

function! SelectSomething()
call fzf#run({
    \ 'source': "my-cmd",
    \ 'sink': ":DoSomething"
    \})
endfunction

```

Here we define a command named `MyCmd`, that will call the
`SelectSomething()` function.

`SelectSomething` in turn will use the output of the `source` argument
as `fzf` input, and then will run the `sink` command on the selected element.

# Consistency is key

To be honest, I must say that I was already using a fuzzy finder named
[CtrlP](https://github.com/kien/ctrlp.vim).

But I decided to stop using it and use `fzf` instead.

That's because s something really nice about using the same tool in my shell and
in my editor. It means I only need to learn how to use and configure it once.

But this goes further than that. For instance, in my setup:

* The `:Files` command uses `<leader>t` in neovim, and the equivalent
  for the shell is `<CTRL-t>`. (same letter)

* There's a `:Gcd` command in `vim-fugitive` and I have a `gcd` command
  in my `.zshrc`  to do the same thing:

```bash
# go to a path relative to the top directory
# of the current git worktree.
function gcd() {
  topdir=$(git rev-parse --show-toplevel)
  if [[ $? -ne 0 ]]; then
    return 1
  fi
  cd "${topdir}/${1}"
}
```

This is not a coincidence. After all, If I'm doing the same kind of stuff in my
editor and my shell, I expect to be able to use similar keystrokes.

{{<note>}}
I've still have a few things to say about the editor/shell relationship,
but this will be done in an other post. (shameless teasing)
{{</note>}}

# Conclusion

So that's my story about `fzf`. It boils down to quite a simple process:

* Find patterns and frictions in the usage of your tools
* Find a generic solution to tackle the pattern you've found
* Try to get consistent configuration and mapping everywhere so that
  things are easier for you to type and remember.

By the way, if this reminds you of the famous [Seven habits of effective text
editing](http://moolenaar.net/habits.html) article by Bram Moolenaar, this is no coincidence either :)

Cheers!
