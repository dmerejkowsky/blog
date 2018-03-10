---
slug: "i-use-vim-and-so-should-you"
date: "2016-03-31T16:10:06+00:00"
draft: false
title: "I Use Vim, And So Should You"
tags: ["neovim"]
---

Actually this is not a post to convince you to use Vim, it's a post to make you
think about your editor and how you use it.

Sorry about the deceptive title :)

There are still some good links at the end if you want to learn Vim or get
better at it.

<!--more-->

# A peer programming story

Back at the office, it sometimes happens we face a really tricky bug and we ask
someone else for help.

One day I was stuck into a tricky bug, and ask a workmate for help. He fired up
`emacs`, (the bastard), and we looked at the code.

After a few minutes, we knew what changes needed to be made ("just call that
before this, add this parameter here, ...")

What followed was a succession of rapid key strokes and text flashing
everywhere. I could barely followed what was going on, until my colleague
stopped and checked the code worked by typing a few lines in an other terminal.

The funny thing is that he described exactly the same thing when he came at my
desk, and watched me refactoring some code too.

# The moral of the story

What is the moral of story?

Thinking about code and actually modifying the code are two very different
things. When you are thinking about the code, you try to keep in your brain the
code structure, the bug you are having, and all the various cases this given
line must support. When you are writing code, you just need to dump your brain
into the text you are seeing on the screen.

Vim and Emacs have a steep learning curve. What this means if that you actually
have to practice long enough so that operations like re-indent, open this file,
look for this function, change this text, become part of your muscle memory.
That's why it's so damn hard to use Vim without your custom settings or your
favorite plugins. [^1]

# Conclusion

It's OK to not use Vim or Emacs. It's not OK to be a slow typist, or not using
the right tool to the job. Being able to write some code **without**
having to think about how I should write it, changed drastically the way I
write code.

It also has a crucial impact on how you handle refactorings. If you start
thinking "Oh, my good, I'm gonna need to open so many files I'm going to have
too many tabs open", you are in a bad place.

I actually love refactoring, because I can let my editor do most of the work
for me. (and also because I have a good test suite, but that's an other story)

So, just take the time to really **learn** the editor. Learn the
shortcuts, learn the menus, learn how to quickly move around and open new
files.

If people can understand what you are doing when you change many code in many
places, you are not good enough. And I've seen people being incredibly
efficient in Emacs, Vim, Eclipse, and even Visual Studio.

That being said, Vim makes it so darn hard to just insert some text that you
**have** to learn it the hard way, (I don't remember any of vim shortcuts
or mapping, they are just in my muscle memory), so it's an excellent choice if
you are not sure.

# Links

To learn Vim:

* [Derek Wyatt Vim's videos](http://www.derekwyatt.org/vim)
* [Drew Neil's VimCast](http://vimcasts.org) Drew Neil also wrote a book that
  has a very good reputation, but I did not read it.
* [The Vim Learning Curve is a Myth by Ben Orenstein](
  https://robots.thoughtbot.com/the-vim-learning-curve-is-a-myth)
* [TupperVim French Vim user group ](http://tuppervim.org)

Before writing your own plugin:

* [Learn Vim Script the Hard Way](http://learnvimscriptthehardway.stevelosh.com/)

[^1]: Speaking of plugins. I'm using the [Ctrl-P](https://kien.github.io/ctrlp.vim) vim plugin, a fuzzy file opener. I can open files by just thinking about what part of the filename I want without knowing exactly where they are located. Seriously, if your editor does not support this kind of feature, it's not worth using.
