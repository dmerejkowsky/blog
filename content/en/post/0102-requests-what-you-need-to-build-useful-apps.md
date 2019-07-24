---
authors: [arj]
slug: requests-what-you-need-to-build-useful-apps
date: 2019-07-24T11:01:01.806215+00:00
draft: false
title: "Requests: What You Need To Build Useful Apps"
tags: [python, guest]
---

_Today's article has been written by guest Abdur-Rahmaan Janhangeer. He is Organising Member of the [Python Mauritius User Group](http://www.pymug.com), Arabic Coordinator for the docs and maintainer of [pythonmembers.club](http://www.pythonmembers.club) and was kind enough to submit this article to be posted there._

Requests is a popular Python library. It has particularly been praised for its intuitive programming API. If you are new to Python, this should be a top priority in your learning path. Today we are going to give you some useful blocks to immediately get started! Have fun!

## Just How Popular Is Requests?

Requests gets [1M+ downloads](https://pypistats.org/packages/requests) per day, yes per day! That's really crazy. It's the lifetime download of an average package! It has also been used among others to help humanity see the first [image of a blackhole](https://github.com/achael/eht-imaging/blob/master/requirements.txt). Sphinx, Celery and Tornado [also use it](https://libraries.io/pypi/requests)!

## How Do Server Requests Work?

Requests get it's name from requests made to servers. Servers always listen for requests to resources. You tell it: give me a packet of sugar, it looks for it, if found, it'll tell: "ok! found it!"" else, it will tell: "oh oh not found". In real life, your browser asks for images, webpages etc. Here are some types of requests:

- GET
- POST
- PUT
- DELETE

The most used type is the GET request. While opening a normal webpage, your browser makes a GET request.

## Comparing Normal Code To Requests Code

Here is what you'll do to get a byte representation of a webpage (which gives the page source).

```python
import urllib.request
content = urllib.request.urlopen("https://dmerej.info").read()
print(content)
```

with requests (it's pip install requests), you do

```python
import requests as r
req = r.get("https://dmerej.info")
print(req.content)
```

req has many attributes to try. Let's explore some!

## Requests Exploration

Try the following in a shell:

```python

>>> import requests as r
>>> req = r.get("https://dmerej.info")
>>> req.text
>>> req.status_code # 200 means ok!
>>> req.reason
>>> req.text
>>> req.content
```

## Start Cooking: Using Beautiful Soup

Here's a BeautifulSoup snippet usage with requests:

```python
from bs4 import BeautifulSoup
import requests as r

req = r.get("https://dmerej.info")
soup = BeautifulSoup(req.content, 'html.parser')
print(soup.text)
```

As a side note, if you have a url like this:

```
http://modifyme.org?name=dimitri
```

you can make a get request like this:

```python
req = r.get('http://modifyme.org', params={'name':'dimitri'})

```

and you will get the same thing.

## Getting JSON data

JSON data are similar to Python dictionaries. Here is a snippet to try out:

```python
import requests as r

req = r.get("https://randomuser.me/api/")
print(req.json())
```

It's an api that generates fake user data. `req.json()` returns a Python dictionary ready to use.

## Download File

Here's a function that downloads a file where you want, given the url:

```python
import requests

def download_file(file_url, path):
    r = requests.get(file_url, allow_redirects=True)
    open(path, 'wb').write(r.content)
```

Since `r.content` returns a byte object, we write the file in `wb` (write binary) mode, thus getting our file. It works for any file url. Try it!

## Upload File

POST requests are used to send data to the server, a typical post requests look like this:

```python
r.post('http://www.example.com/verify_login', data={'name':'moi', 'password':'1234'})
```

Let's say while disseting a form you get a form using POST to upload a file which looks like this:

```html
<form action="/upload" method = "POST"
enctype="multipart/form-data">
<input type="file" name="file_to_upload" />
<input type="submit"/>
</form>
```

We can write a script like this to upload a file, an image in this case:

```python
import requests as r

files = {'file': open('<path_to>/image.png', 'rb')}
req = r.post("http://www.example.com/upload", files=files)
print(req.text)
```

The above snippet is useful if you have to upload to your own custom backend. But, in the real world, sites add some input values with different name attributes to detect automatic submissions and you might have to modify to

```python
r.post("http://www.example.com/upload", files=files, data={'<name>':'<value>',})
```

## Caveats To Look For

It should be born in mind that requests does not execute the JavaScript on a web page. If you are doing webscraping, there are other tools like Selenium.

Requests in an incredible tool to add to your arsenal, make good use of it!





