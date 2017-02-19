---
slug: of-pythons-and-cats
date: 2017-02-19T14:11:44.334579+00:00
draft: true
title: Of Pythons and Cats
---

Today I want to talk about implementing `cat` in Python.

The goal is just to dump the contents of a file to the terminal.

Should be pretty simple, right?

Well, let's have a look.

We'll try to handle all the corner cases we can think of, first in
Python2, and then in Python3.

Ready? Let's go!


## Using Python2

Let's write our first version in Python2, and try it on linux:

```python
# in cat.py
import sys

with open(sys.argv[1]) as f:
  print f.read()
```

Let's try:

```console
$ echo "this is foo" > foo.txt
$ python cat.py foo.txt
this is foo

$ cat foo.txt
this is foo
```

### Fixing the extra new line

Right away, we get our first bug. `print` added an extra new line.

We can fix this by using trailing coma

```python
import sys

f = open(sys.argv[1])
print f.read(),
```

Let's try the same code on Windows (using the default Powershell
configuration)

```console
> c:\Python27\python.exe .\cat.py .\foo.txt
This is foo
```

### Adding some coffee.

Now, let's add some non-ASCII characters in the text file.

On Linux:

```console
$ echo "J'aime le café" > foo.txt
$ python2 cat.py foo.txt
J'aime le café
```

Note: here we are using a 'modern' linux distribution, so `foo.txt` is
UTF-8 encoded.

On Windows, let's try, *using the same foo.txt file*:

```console
> c:\Python27\python.exe cat.py foo.txt
J'aime le caf├⌐
```

Uh-oh. Something is not right.

We open `foo.txt` in `Notepad++` and we see that the encoding is `UTF-8`.

That's not the encoding used by Windows, so let's try to find an encoding that
works.

First, we'll write the `café` string in `foo.txt` directly from powershell,
overriding the previous contents:

```console
> echo "café" > foo.txt
> type foo.txt
café
```

OK, that works. Let's try to patch the Python code.


`Notepad++` tells us the file is encoded in "UCS-2 LE BOM", which
is an other way of saying "UTF-16".

Also `sys.stdout.encoding` is `cp437`.

So, basically we need to convert the UTF-16 string written by powershell
to a unicode object that python will hopefully know how to print:

```python
with open(sys.argv[1], "rb") as f:
	data = f.read().decode("utf-16")
	print(data),
```

Or, alternatively:

```python
import codecs

with codecs.open(sys.argv[1], "r", "utf-16") as f:
	data = f.read()
	print(data),
```


### Breaking cat.py

Let's write just the string `café` in the file
and use `wc` to count the number of characters:

We expect to get 5 (4 letters and the newline character):

```console
$ echo café > utf-8.txt
$ wc -c utf-8.txt
6 utf-8.txt
```

#### Changing file encoding

To "fix" this we can try using an encoding that will use
only one byte to encode the `é`, such as ISO-8858-15:

```console
$ iconv -f UTF-8 -t ISO-8859-15 foo.txt > iso.txt
$ wc -c iso.txt
5 iso.txt
```

OK, it works. But now if we try to use `cat.py`, we get

```console
$ python2 cat.py iso.txt
caf
```

Hum. Python just silently failed. Let's fix this by using `codecs` again:

```console
import sys
import codecs

with codecs.open("iso.txt", "r", "iso-8859-15") as f:
    data = f.read()
    print(data),
```

```console
$ python2 cat.py iso.txt
café
```

#### Changing terminal encoding

We can still break our `cat.py` program by telling our terminal to assume
a different encoding:

```console
$ luit -encoding ISO-8859-1
$ python2 cat.py utf-8.txt
cafÃ©
```

In UTF-8, `é` is encoded with two bytes, but ISO assumes one character per byte,
hence the replacement of the letter `è` by two letters, `Ã` and `©`.

### Python2 conclusion

OK, so what did we learn?

* There are no good way to use `print` without it having appending a new line.
  Of course, we could have used `sys.stdout.write()`, but still.
* The Python code we wrote can *silently fail* in various ways, either because
  we change the encoding in the filenames, or the encoding of the terminal.
  In both cases, we had to use `codecs.open()` instead of `open()`, or call
  `data.decode()`


## Python3


Here's what the Python3 version looks like

```python
import sys

with open(sys.argv[1]) as f:
    print(f.read(), end="")
```

Cool, we no longer need a trailing coma, because `print` is now a function and
we can explicitly say we _don't_ want a trailing newline :)


### Linux

Let's try it with the `utf-8.txt` file:

```console
$ python cat.py utf-8.txt
café
```

OK, it works. Now let's try with our "ISO" file:

```console
 File "cat3.py", line 4, in <module>
    data = f.read()
  File "/usr/lib/python3.6/codecs.py", line 321, in decode
    (result, consumed) = self._buffer_decode(data, self.errors, final)
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 3: invalid continuation byte
```


Cool, instead of silently failing we get a nice error telling us _exactly_ what
happened.

We tried to read the content of the file `data=f.read()`, but we were using
`utf-8` codec and the byte `0xe9` is the 3rd position was unexpected.

You see, `utf-8` has rules to be able to encode single characters (such as `è`)
as two bytes. So some sequences of bytes are _not_ UTF-8 valid strings, and
Python just told us that.

The fix is obvious: we had a `UnicodeDecodeError`, so we need to decode using an
other encoding:

```console
import sys
with open(sys.argv[1], "rb") as f:
    data = f.read()
    data = data.decode("ISO-8859-15")
    print(data, end="")
```

Or, alternatively:


```console
import sys
with open(sys.argv[1], "r", encoding="ISO-8859-15") as f:
    data = f.read()
    print(data, end="")
```

But wait! Are we _really_ sure that's what we want?

Maybe we _do_ want the *exact bytes* of the file to be dumped to the screen.

Well then, we should not use `print()`, which is for *strings*, but
`sys.stdout.buffer`, which is where we can write raw bytes:

```console
import sys
with open(sys.argv[1], "rb") as f:
    data = f.read()
    sys.stdout.buffer.write(data)
```

Cool, we get the same behavior as the `cat` command:

```console
$ python3 cat.py iso.txt
caf�
$ python3 cat.py utf-8.txt
café

$ cat iso.txt
caf�
$ cat utf-8.txt
café
```

### Windows

```console
PS C:\Users\Administrator\Desktop> C:\Python36\python.exe .\cat.py .\foo.txt
Traceback (most recent call last):
  File ".\cat.py", line 5, in <module>
    data = f.read()
  File "C:\Python36\lib\codecs.py", line 698, in read
    return self.reader.read(size)
  File "C:\Python36\lib\codecs.py", line 501, in read
    newchars, decodedbytes = self.decode(data, self.errors)
  File "C:\Python36\lib\encodings\utf_16.py", line 141, in decode
    raise UnicodeError("UTF-16 stream does not start with BOM")
UnicodeError: UTF-16 stream does not start with BOM
```
