---
authors: [dmerej]
slug: neovim-cwd-nerdtree-and-ctrl-p
date: 2016-12-17T12:27:56.733729+00:00
draft: false
title: Neovim, cwd, NERDTree and CtrlP
tags: [neovim]
---

A follow-up to my [latest article]({{< relref "post/0008-vim-cwd-and-neovim.md" >}})
where I explain how I made further changes to make things
work with [NERDTree](https://github.com/scrooloose/nerdtree) and
[CtrlP](https://github.com/ctrlpvim/ctrlp.vim)

<!--more-->

## Previously on this blog

I like the idea of having one tab per project, and one working directory
per tab.

In a way, you could say I like managing my working directory myself,
like using a manual transmission instead of an automatic car.

Thus I've added several shortcuts like:

* `<leader>cd`, or `<leader>ew` to go to the parent directory of the file being edited, using
  `:lcd` instead of `:cd` so that I do not change the working directory
  on every tab and window.

* `<leader>ew`, to edit the file next to the one I'm currently editing, without
  to temporary change the working directory.

I also used the new `TabNewEntered` event from `Neovim` to change
working directory upon tab creation:

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

This worked great until I realized `NERDTree` was messing things up.

## NERDTree and events

For some reason[^1], when `NERDTree` is installed, the event does not get
triggered with the correct path.

When going from `~/src/blog` to `~/src/foo`, the `OnTabEnter` function
gets called with the old path, even though `NERDTree` shows `~/src/foo` instead.

The culprit seems to be those lines:


```vim
if g:NERDTreeHijackNetrw
  augroup NERDTreeHijackNetrw
    autocmd VimEnter * silent! autocmd! FileExplorer
    au BufEnter,VimEnter * call nerdtree#checkForBrowse(expand("<amatch>"))
  augroup END
endif
```

Fortunately, there's a way to disable `NERDTree` behavior:

```vim
let g:NERDTreeHijackNetrw = 0
```

## Opening NERDTree

But now `NERDTree` no longer opens by default when I edit a directory.

There's a `:NERDTree` command, but it opens in a split window and I
don't want that: I want the `NERDTree` window to replace the window of the file
I'm currently editing.

Why?

Because for me, `vim` is all about doing several things _without_ moving your eyes
or your hands to much.

Let's say I'm in a middle of editing `foo.py` and I need to open a file
for some reason (realized I need to patch an other file, or look for the
implementation of a function I'm using), I will use `:e` or `<leader>b` so that
the old buffer contents gets _replaced_ by the new, and then I can come back to
`foo.py` without loosing focus.

For me browsing the file system looking for things, or creating a directory in
the correct place for a new file I want to write is not worth breaking the flow.

If I'm okay with breaking the flow, I'll consider using a split (for fixing a
test&nbsp;...), or a tab if I'm doing something completely different (a new
feature, patching the changelog&nbsp;...), or even closing `vim` and re-open it
from an other terminal window.

Thus I patched[^2] `NERDTree` so that it would not try to create a split:
```diff
diff --git a/lib/nerdtree/creator.vim b/lib/nerdtree/creator.vim
index 89f03a3..cd67cfd 100644
--- a/lib/nerdtree/creator.vim
+++ b/lib/nerdtree/creator.vim
@@ -194,14 +194,11 @@ function! s:Creator._createTreeWin()

     if !exists('t:NERDTreeBufName')
         let t:NERDTreeBufName = self._nextBufferName()
-        silent! exec splitLocation . 'vertical ' . splitSize . ' new'
         silent! exec "edit " . t:NERDTreeBufName
     else
-        silent! exec splitLocation . 'vertical ' . splitSize . ' split'
         silent! exec "buffer " . t:NERDTreeBufName
     endif

-    setlocal winfixwidth
     call self._setCommonBufOptions()
 endfunction
```


After that, I wrote a new function and a defined a mapping to call it:

```vim
function! NerdTreeInPlace(path)
  :execute "NERDTree " . a:path
endfunction

nnoremap <leader>r :call NerdTreeInPlace(getcwd())<cr>
```

## Closing NERDTree

I now had a binding for opening `NERDTree` but then it's complicated to
close the `NERDTree` window: since no other buffer is open, using `q` does not work.

So I had to make sure I could go to the previous buffer, using
the same key strokes: toggling is fun and only requires me to remember one
shortcut :)

But how to make sure I could get back where I came from?

Easy, use marks!

In `vim`, you can set marks in command mode by using `m` followed by a letter.
To get back to the previous mark, use a back tick:

```text
ma
`a
```

This works across files providing the letter is uppercase.

So that's what the function looks like now:


```vim
function! ToggleNerdTreeInPlace(path)
  if bufname("%") =~ "NERD_tree_"
    :normal! `N
  else
    :nomal! mN
    :execute "NERDTree " . a:path
    :only
  endif
endfunction

nnoremap <leader>r :call ToggleNerdTreeInPlace(getcwd())<cr>
```

(I use the letter `N` so that I can still use global marks from A to M if I want to)

An other annoying thing for me is that by default `NERDTree` will
open files in a new window, keeping the directory view opened.[^3]

You can also fix that by using:

```vim
let g:NERDTreeQuitOnOpen = 1
```

There! Now if you type `o` or `enter` when browsing files, the `NERDTree` window
will close.

## Fixing CtrlP

By default `CtrlP` tries to guess the "project root dir", by
looking for directories like `.git`, `.bzr` and such in the upper directories.

So if my working directory is `src/foo/doc` and I want to look for a documentation file,
`CtrlP` will show me all the files in `src/foo`, which again, is not what I
want. (Remember, I prefer manual transmission to automatic).

You can prevent `CtrlP` from being too smart by disabling this feature
completely:

```vim
let g:ctrlp_working_path_mode = ""
```

And, if you _do_ need to get back to the root of your `git` project, you
can use:

```vim

function! CdTop()
  let topdir=system("git rev-parse --show-toplevel")
  :execute ":lcd " . topdir
endfunction

command! CdTop call CdTop()
```

Or, if you use [vim-fugitive](https://github.com/tpope/vim-fugitive),
you can use `:Gcd` or `:Glcd`

By the way, I have the same kind of function in my `zshrc`:


```bash
function gcd() {
  topdir=$(git rev-parse --show-toplevel)
  if [[ $? -ne 0 ]]; then
    return 1
  fi
  cd "${topdir}/${1}"
}
```

Coincidence? I think not!

[^1]: It may be a `Neovim` bug, I'm not sure yet.
[^2]: I may upstream the patch later, but this will involve adding a new configuration option, and I'm not sure upstream is OK with that.
[^3]: I've explained why in the previous paragraph, try to keep up!
