+++
date = "2016-04-30T12:38:17+00:00"
draft = false
title = "Vim, cwd, and Neovim"
+++

This is quite a long post on the topic of working directory and (Neo)vim.

There will be a second part to this story, and maybe a `TLDR;` if
you ask nicely :)

<!--more-->

# Introduction: what is the cwd ?

## In a command line prompt

`cwd` is short for "current working directory".

Every command you run has its own current working directory. When you start a
terminal emulator, your first `cwd` is your home directory (`/home/user`), and
then you can use `cd` to change the working directory.

At any time you can display your working dir by typing `pwd`, and usually your
prompt is configured to give you this information.

Here the prompt is configured to display the working directory between square
brackets:

```bash
[/home/user] $ pwd
/home/user
[/home/user] $ cd /foo/bar
[/foo/bar] $ pwd
/foo/bar
```

Setting the working directory allows you (among other things), to type relative
paths instead of full paths.

For instance, let's assume you have some `C` code in `/path/to/foo/src`, you
need to edit the source code for
`bar` and its header.

You could run:

```bash
[/home/user] $ vim /path/to/foo/src/bar.c
[/home/user] $ vim /path/to/foo/src/bar.h
```

But it's much more convenient to use:

```bash
[/home/user] $ cd /path/to/foo/src
[/path/to/foo] $ vim bar.c
[/path/to/foo] $ vim bar.h
```

## In Vim

Vim is no different. When you start vim, it gets the working directory of your
shell. And then you can type commands like
`:e` to open paths relative to your working directory.

Using the same example, after:

```bash
[/home/user] cd /path/to/foo/src
[/path/to/foo] vim
```

you can run `:e bar.c`, and then `:sp bar.h`

## The problem: working with several directories

This is all well and good, but what happens when you start working on
**several** projects ?

For instance, you could be working on the HTML documentation of your project,
in `/path/to/foo/doc`.

You need to see the `.html` and `.css` files when you are editing the
documentation, but also sometimes you want to have a look at the actual code.

An obvious solution is to create a new tab, with `:tabnew doc`, but then if you
want to edit `index.html` you have to type
`:e ../doc/index.html`.


An then if you want to edit the CSS you have to run: `:vs ../doc/style.css`

So you have to keep typing `../doc/` and it's annoying.

## My journey to the prefect workflow

I've got this issue for **years**. It's taken me a long time to find a solution
for this problem, so I thought I'd share this process with you.

### Step 1: using autochdir

Vim has an option for this. Here's the documentation:

<pre>
'autochdir' 'acd'	boolean (default off)
			global
	When on, Vim will change the current working directory whenever you
	open a file, switch buffers, delete a buffer or open/close a window.
	It will change to the directory containing the file which was opened
	or selected.
	Note: When this option is on some plugins may not work.
</pre>

That was my first try.

I think it's not a good solution (and not only because it's what Emacs does
this by default :P)

Here's why.

Let's assume your project became more complex, and you start having a
subproject called `baz`.

Here's what your source code looks like:

<pre>
&lt;foo&gt;
  src
    bar.h
    bar.c
    baz
        baz.c
   doc
      index.html
      baz
          baz.html
</pre>

When you are editing `bar.h`, you can type `:e baz/baz.c` and it feels natural.

But then, if you want to go back from `baz/baz.c` to `bar.h`, you have to use
`:e ../bar.h` which feels strange...

Worse, let's assume you have:

```C
/* in baz/baz.h */
#include <bar.h>

```

You may want to open `bar.h` by using `gf`, or auto-complete the path to the
header using `CTRL-X CTRL-F`, but you can't since you don't have the correct
working directory!

Plus the doc says it may break some plugins...

### Step 2: using :cd

Vim has a command to change the working directory as well.

So back to our example, you can do:

<pre>
:cd /path/to/foo
:cd src
:e bar.c
:e baz/baz.h
:tabnew
:cd ../doc
:e index.html
</pre>

Well that's much better! There's still a problem though: `:cd` changes the
working directory for the whole vim process.

So if you run `tabprevious` to go back editing the `C` code, your working
directory is no longer correct, and you have to re-type `:cd src`.

### Step 3: using :lcd

Luckily, vim has a command to change the working directory just for the current
window: `:lcd`. So I started using that.

And then I realized I often started vim directly from my home directory, so I
had to type things like:

<pre>
:e /path/to/foo/src.c
# Ah, I need to change the working directory...
:cd /path/to/foo/
</pre>

That's awful. You type the same path twice!

Or I used to type:

<pre>
:cd /path/to/foo/src
:e foo.h
# Time to fix the doc
:tabnew ../doc
:cd ../doc
# Ah crap, I meant :lcd ...
</pre>

### Step 4: using a custom command

I don't recall how I found it, but here's what has been in my `.vimrc` since
quite some time:

```vim

" 'cd' towards the dir in which the current file is edited
" but only change the path for the current window
map <leader>cd :lcd %:h<CR>
```

Explanation:

* `map` defines a new command
* `leader` is replaced by what you set with `let mapleader`. Default is
  backlash, but you can use any character for this.
* `lcd` is the command we just talked about
* `%` represents the current file, and what's after the `:` is called a
  "filename modifier"
* `h` is a filename modifier corresponding to the ''dirname'' of the file

You can see the full list of filename modifiers with `:help
filename-modifiers`, and to use them from vimscript you can use the
`fnamemodify()` or `expand()` functions.

Well, that's much better. You can start opening a long path, and then change
the working dir without retyping all the path components.

Also, you are always using `:lcd`, so you never change the path globally.

This quickly became **the** shortcut I could no longer live without...

### Step 5: using &lt;leader&gt;ew

This is another trick you can use when you know are going to edit a file that
is "near" the file you are currently editing, but don't
want to change the working directory at all.

The code looks like this:

```vim
" Open files located in the same dir in with the current file is edited
map <leader>ew :e <C-R>=expand("%:p:h") . "/" <CR>
```

Explanation:

* `<C-R>=` is short for `Ctrl-R` followed by the _equals_ sign. It allows to
  enter a vim _expression_.
* `expand(%:p:d)`: we see our `%` friend, which still represents the current
  filename
* `:p:h`: two file modifiers: one to get the full path (`:p`), and the other to
  find the dirname (`:h`)
* Then we add a `/` so that we can start typing the filename right away.

Here's how you use it

<pre>
:e /some/long/path/to/foo.c
&lt;leader&gt;ew foo.h
# opens /some/long/path/to/foo.h
</pre>

### Step 6: using :TabNew

After a while, I realized I really liked having one working directory per tab.
I found myself typing stuff like:

<pre>
:tabnew /some/path
:e some-path-at-the-top
<leader>cd
:e subdir/otherfile.c
</pre>

I was opening a file at the top of the project **just** to be able to use my
`<leader>cd` command and start thinking of better ways.

So finally I came up with a new command:

```vim
" Change local working dir upon tab creation
function! TabNewWithCwD(newpath)
  :execute "tabnew " . a:newpath
  if isdirectory(a:newpath)
    :execute "lcd " . a:newpath
  else
    let dirname = fnamemodify(a:newpath, ":h")
    :execute "lcd " . dirname
  endif
endfunction

command! -nargs=1 -complete=file TabNew :call TabNewWithCwD("<args>")
```

Hopefully by now you should understand what this does: I create a function that
calls `fnamemodify` to get the dirname of the file
I want to open in a new tab, and then calls `:lcd` with the correct argument.

### Step 7: Switching to Neovim

And then I switched to [Neovim](http://neovim.io), and two things happened:

* 1/ Neovim folks added the `TabNewEntered` event
* 2/ They also added the `tcd` command, which allows to change the working dir
  just for a tab.

That's **exactly** what I needed!

So now my vimrc looks like:

```vim

function! OnTabEnter(path)
  if isdirectory(a:path)
    let dirname = a:path
  else
    let dirname = fnamemodify(a:path, ":h")
  endif
  execute "tcd ". dirname
endfunction()

autocmd TabNewEntered * call OnTabEnter(expand("<amatch>"))
```

So no matter how I enter a new tab, my working directory is automatically set
to the correct location, and when I switch tabs I switch working directories
too. Perfect!


### Step 8: Fixing vim-fugitive

To conclude my journey, I'd like to share just a tiny bug fix I had to do for
using [vim-fugitive](https://github.com/tpope/vim-fugitive])

It occurred when I was working in a git project, with the Python code in
`python/`, and the documentation in `doc/`.

I was in my `python/` tab, ran `:Ggrep` and suddenly I got results for **all**
the files in the repositories, including the documentation.

That's because `:Ggrep` starts by changing the working directory to the top
directory of the current git repository.

Fortunately the fix was easy, here's my
[pull request on github](https://github.com/tpope/vim-fugitive/pull/787).

I don't know if it will be accepted by Tim Pope, but I hope that now you
understand why this is such a big deal for me :)

Thanks for reading!
