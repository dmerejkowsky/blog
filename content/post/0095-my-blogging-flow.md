---
authors: [dmerej]
slug: my-blogging-flow
date: 2019-02-06T11:46:32.632044+00:00
draft: false
title: "My Blogging Flow"
tags: [blog]
summary: How this blog gets written
---

Several people ask me how my blog works and how it gets written, so here's a blog post about how I blog (so meta).

# History

## Getting my own machine

I always wanted to control all aspects regarding the hosting of my blog, so I started by buying a dedicated machine from a company called `dedidox` (it was not called 'in the cloud' yet). Since then, dedibox has been bought and his name changed (twice!) and I  moved to a [Digital Ocean](https://www.digitalocean.com/) droplet.

Anyway, after I got my own dedicated machine with `ssh` and `nginx` it was time to start looking for a blog engine.

## Static or dynamic

There are two types of blog engines: "static" and "dynamic". It has to do with what happens when a visitor requests the article's URL.

In a dynamic blog engine, the contents of each article are typically stored in a database, and the HTML is generated "dynamically" by the engine for each visitor.

On the other hand, a "static" engine typically generates a whole bunch of HTML files from sources written in a markup language (often Markdown). Then all you have to do is to serve the correct file when a visitor wants to view an article.

Both of them have pros and cons:

* Dynamic blog engines can handle comments, compute statistics (like view count), but they need a programming language (often php) and some code running on the server.

* Static blogs cannot handle comments or anything like that, but they are *very easy* to deploy and you can directly use existing web servers (like `nginx` or `apache`).

## Finding a blog engine

I must say I spent way too much finding the engine I would use for my blog.

My guts told me I wanted a static engine, so I started fiddling with many static blog generators. Alas, they are *tons* of static engines out there, and I almost gave up on finding the one I would use - there were simply too much choice.

That's when I realized I was not tackling the problem correctly: I was worried on *how to publish contents*, but said content was *yet to written!*

So I look at dynamic blog engines, found out about Wordpress and Dotclear, chose Dotclear almost randomly, and started writing.

Finally, my contents were online and publicly readable by anyone on the world. What a joy!

Advice to my dear readers: if you want to publish something online, please don't make my mistake: make sure you *have* contents before worrying about its publication.

## The dotclear period

Configuring `php` for Dotclear was a bit tedious, but once it was done I must say it was quite pleasant to use. The admin view is rich and featureful, and the editing form is ergonomic. Comments are supported out of the box, and they are easy to moderate.

But I still I had a problem: I was receiving many notifications about comments but *almost all of them were spam* :/

This was depressing, so I shot down the comment service and started looking for an alternative.

## The hugo period

I went back looking for static engines, and found `hugo` on [the StaticGen comparator](https://www.staticgen.com/) comparator.

I immediately liked it:

* There are many beautiful themes available. (Dotclear themes are nice too, but they looked a bit old to me).
* `hugo` is easy to install (just one binary)
* Its documentation is complete and easy to follow
* And I no longer had to try and configure `php` on my server. Just a few lines of `nginx` configuration was enough.

Hugo does not come with a default theme, so after a few tries, I settled on using [blackburn](https://themes.gohugo.io/blackburn/).

I was quite happy with it for a while. Article after article, I had to make a few tweaks and learned a bit about the joys of CSS.

### Writing my own shortcode

I still remember fondly the day I managed to implement the "movie script look" for the short scenes I wrote in [Heard and Seen at FOSDEM 2017]({{< ref "post/0034-heard-and-seen-at-fosdem-2017.md#scenes" >}}).

Here's how it works.

First, I have custom `scene` shortcode insid the `layouts/shortcode` directory of the theme:

```go-html-template
<div class="scene">
<h1>
  {{ .Get "title" }}
</h1>
{{ .Inner | markdownify }}
<p>
</div>
```

This allows me to write things like this in the Markdown source:

```markdown
{{< scene title="Resurrecting Dinosaurs, what could possibly go wrong?" > }}
SPEAKER: I did *not* expect to have a win32 architecture slide here at FOSDEM
{{< /scene >}}
```

When hugo sees the `{{< scene` directive it will generate the html with:

* The `<div>` and its special `scene` class
* The `title` inside the `h1` tag
* And the text inside the `{{< scene >}}` directive, interpreted as Markdown too

Finally, I have a bit of CSS to render the `div` properly:


```scss
.scene {
  font-family: monospace;
  line-height: 1.2em;

  h1 {
    line-height: 1.5em;
    font-size: 1.2em;
    font-style: bold;
    text-align: center;
  }
}
```


### Switching to a new theme

After a while, I was getting tired with `blackburn`. Its CSS files were not easy to patch, and it had a dependency to `font-awesome`, which is convenient for quick and dirty logos or icons, but leads to a bit of ugly html.

So I switch to `minio`, which is the theme I still use today. It uses `sass` instead of pure `CSS`, and its sources are neatly organized. Plus, it comes with a nice `package.json` which allows to "watch" changes made to the theme instantly.

## Source organization

If you take a look at the [sources of the blog](https://github.com/dmerejkowsky/blog/tree/master/content/post) you will find posts are numbered chronologically. I like this scheme for several reasons:

* Posts naturally appeared sorted everywhere (even with `ls`)
* I will get this nice feeling of accomplishment when I write my 100th post
* I can easily autocomplete filenames from my editors (I just need to remember the post number)

Since I don't really want the internal number to be seen outside, all the articles have a `slug` in the "front matter":

```markdown
# In 0042-foo.md
---
slug: "foo"
date: "2016-03-31T13:00:19+00:00"
draft: false
title: "..."
---
```


So that's how the blog works under the hood. Now, allow me to explain how the publication works.

# Publication flow

Everything starts with an idea. I have a small git repository on my dedicated machine which contains a bunch of markdown files, one per article. (This repository is private by the way).

The contents of these files can vary from just a few lines, to an almost complete article. Most of the time they only contain a basic outline though.

I update the `ideas` repository as soon as ideas come. You won't believe how fast you can forget what or how you wanted to say something otherwise.

Next it's time to start writing the full article. I have a [small Python script](post.py) which:

* finds out the next article number and fill up the front matter for me (because I'm lazy)
* runs `git add` on the generated Markdown file so I don't delete it by mistake by running `git clean` (because mistakes happen)
* opens the Markdown file in Neovim

Now it's time to draft the article. I always do it from Neovim
