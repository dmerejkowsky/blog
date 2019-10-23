---
authors: [dmerej]
slug: syntax-highlighting-is-useless
date: 2018-10-04T13:30:31.118512+00:00
draft: false
title: "Syntax Highlighting Is Useless"
tags: [neovim]
summary: Why I turned off syntax highlighting for Markdown files.
---

&hellip; at least when it comes to Markdown files ;)

# Introduction: editing this blog in Neovim

Here's what it used to look like to edit one of my articles in Neovim:

![Colored markdown file in Neovim](/pics/markdown-colored.png)

Take a quick look. Do you see what's wrong?

* First, the line about the `summary` in the front matter is colored in green. The front matter uses YAML syntax, but Neovim does not know it and thus highlights this line incorrectly.

* Second, the python code is OK, but the language name is misspelt: `pyton` instead of `python`. I *am* using Neovim's built-in spell checker, but since Neovim "knows" the stuff after <code>```</code> is source code, it disables spell checking for this part of the text.

* Third, the link to 'Using CMake and Ninja' is built using [hugo syntax](https://gohugo.io/functions/ref/), and if you were extra careful you may have noticed that the path to the article after `ref` starts with a double quote (`"`), but ends with a single quote (`'`).


# Turning syntax highlighting off


For quite some time I did not think to much about this situation, until I read *[A case against syntax highlighting](http://www.linusakesson.net/programming/syntaxhighlighting/)*, by Linus Åkesson.

So one day I decided to try and turn the syntax highlighting off:

![Un-colored markdown file](/pics/markdown-plain.png)

* This time, the spell checker checks *everything*, and the typo in `pyton` is caught.
* The "rendering bug" of the front matter is gone.
* Also, he problem with the single quote is more obvious to spot. It's less likely to be distracted by all the colors. That one may be subjective: it's what my guts tell me, though.

One more thing: I'm also viewing the rendered HTML in a browser next to my Neovim window. Hugo rebuilds the page I'm editing after each save, and the browser automatically reloads.

This has several consequences:

* First, some parts of the highlight are redundant. I'm able to see the italics in the browser, I don't need to *also* view them as such in the editor.

* Second, the problem with the `{{ref` usage gets caught by the `hugo` process itself:

```
ERROR 2018/10/04 16:36:23 error processing shortcode
  "_internal/shortcodes/ref.html"
  for page "post/0087-demo-syntax-highlight.md":
    template: _internal/shortcodes/ref.html:1:89:
    executing "_internal/shortcodes/ref.html" at <0>:
    invalid value; expected string
```

So let's think about what we learned:

* The syntax highlighting is buggy, and it will never be as good as the HTML rendering. (Especially with Markdown, where each rendering tool has its own quirks).
* It "hides" important information, like spelling errors

So, why do we keep using it?

# Conclusion

For now, I'm just turning syntax off for Markdown files. Here's the relevant section in my `init.vim` file:

```
augroup textfiles
  autocmd!
  autocmd filetype markdown :setlocal spell spelllang=en | syntax clear
augroup end
```

I'm still using syntax highlight in the other cases.

But, in the same way the syntax highlighting may be useless (and even harmful) for editing Markdown when a HTML renderer can be used, maybe syntax highlighting is *also* useless if [a linter can be used directly]({{< ref "/post/0047-lets-have-a-pint-of-vim-ale.md" >}}) to check the code **while it's being typed**.

Food for thought &hellip;
