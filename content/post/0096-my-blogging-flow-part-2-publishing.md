---
authors: [dmerej]
slug: my-blogging-flow-part-2-publishing
date: 2019-02-07T12:14:20.273365+00:00
draft: true
title: "My Blogging Flow - Part 2 - Publishing"
tags: [misc]
summary: How this blog gets written - part 2
---

# The Idea

Everything starts with an idea. I have a small git repository on my dedicated machine which contains a bunch of markdown files, one per article. (This repository is private by the way).

The contents of these files can vary from just a few lines, to an almost complete article. Most of the time they only contain a basic outline though.

I update the `ideas` repository as soon as ideas come. You won't believe how fast you can forget what or how you wanted to say something otherwise.

# The first draft

Next it's time to start writing the full article. I have a [small Python script](post.py) which:

* finds out the next article number and fill up the front matter for me (because I'm lazy)
* runs `git add` on the generated Markdown file so I don't delete it by mistake by running `git clean` (because mistakes happen)
* opens the Markdown file in Neovim

Now it's time to draft the article. I always do it from Neovim with:

* spell checker activated
* syntax highlighting disabled (I've explained why [in a previous blog post]({{< ref "post/0087-syntax-highlighting-is-useless.md" >}}).

In an other terminal (usually hidden behind a tab), I have `hugo serve` running, and finally, next to the text editor, a web browser, so that I can see the changes happening **in real time**.

# Proofreading

And then it's time to proofread, proofread, proofread ...

I usually wait for a good night's sleep before re-reading an article.

If the article is really big and complex, I sometimes open a pull request on GitHub and ask friends or colleagues to review it.

I do my proofread both in Neovim and it the browser, to increase the chance I'll see spelling errors, awkward formulations, transitions problems and the like.

# Publishing

I have an other Python script to automate publication. Here's what it does:

* Make an automatic commit in case I forgot (the script just skips this part if the repository is clean)
* Run `hugo --buildDrafts=false` to build the HTML files
* Run `rsync` to upload them to my server

Note that the publishing of a new post triggers a new version of [the blog feed](/index.xml) to be written.

I then can run yet an other Python script to:

* Parse the RSS feed and find out the URL and title of the latest article
* Make an automatic tweet like [this one](https://twitter.com/d_merej/status/1092029859864416259) (the additional hash tags at the end are given on the command line)
* Ditto for Mastodon
* Finally, send an-email to the people who subscribed to [the newsletter]({{< ref "post/0031-introducing-dmerej-newsletter.md" >}}).
 
# dev.to

Then it's time to wait until `dev.to` picks up the latest version of the RSS feed, parses the HTML from the feed, converts it back to markdown and add it into my dashboard.

(Yup, you can configure `dev.to` to do this!)

This works quite well given the weird round-trip through HTML. Still, I have to re-read the markdown created by the dev importer just in case. This gives me a final opportunity to proofread the article one last time.

# Feedback

Thanks to isso I get notified when new comments are posted. I also of course get notifications from dev.to.

When I'm lucky, `@thepracticaldev` tweets a link to my article, and I get new followers and more views. This is nice :)

That's all folks! If you have any other question regarding how the blog words, don't be afraid to ask in the comments below!
