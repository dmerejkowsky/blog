---
date: "2016-09-17T15:49:38+02:00"
draft: false
summary: |
  What happens when you use `npm` in a cross-platform environment?

  Let's find out in this short story, based on actual events...

title: "An npm Story"
aliases: ["post/a-npm-story"]
---

Let's say you have a cross-platform `C++` application (Linux, Mac, Windows).

Convinced that using web technologies to implement the GUI is a good idea[^1],
you start writing some `javascript`, `css` and `html` code that would run in a
`QtWebEngine` window.

<!--more-->

## Choosing your tools

It's a brand new project, so you decide you're going to use:

* [nodejs](https://nodejs.org/en/) so that you can quickly view
  the rendering of the `html`, `css` and `js` files in the browser.
* [react](https://facebook.github.io/react) and [redux](http://redux.js.org/)
  for the GUI
* [mocha](https://mochajs.org/) for the automatic testing
* [sass](http://sass-lang.com/) because writing `CSS` manually is painful
* [webpack](https://webpack.github.io/) so that you can
  generate static assets that will be integrated in the GUI

Obviously, this means you end up with quite a few `javascript` dependencies,
so you write a `package.json` and start using [npm](https://www.npmjs.com)
to fetch them.

You also read about [why we should stop using grunt](
https://www.keithcirkel.co.uk/why-we-should-stop-using-grunt/), so
you patch the `package.json` to have something like

```json
{
  "dependencies": {
      "webpack": "latest",
  },
  "scripts": {
      "build": "webpack src/*.js"
  }
}
```

And since you do care about build reproducibility, you use
[shrinkwrap](https://docs.npmjs.com/cli/shrinkwrap) so that you don't
accidentally pick up unwanted library upgrades.


So you run `npm install shrinkwrap`, `npm shrinkwrap`, and you push
the generated `npm-shrinkwrap.json` (that contains all the libraries names and
version numbers) to the remote `git` server.

Of course, because you're a front-end developer, you earn enough money to afford
a shiny Apple laptop to hack on your code.

But what happens when you try to use all this shiny new technology on Windows?


## fsevent not found

One member of your teams, working on Windows, then needs to build the static
assets on his machine.

"Easy", you say, "just run `npm install`, then `npm run build` and you're all
set!"

But, after he installs `node`, and runs `npm install` he tells you he
got an error stating that `fsevent` is not available for hist platform.

`fsevent` is actually an optional dependency, but because you generated
the `npm-shrinkwrap.json` file on your mac, `npm install` tries to install it.

This is a [known npm bug](https://github.com/npm/npm/issues/2679), and it seems
the only workaround is to somehow patch the generated `npm-shrinkwrap.json` file
to remove the dependencies you do not care about.

## A workaround

"All right", you say, "I'm just going to write a script that will patch the
generated file, and the team members working on Windows will just have to run it
from time to time".

"It does not really matter, because all those Windows devs are back-end
developers anyway ..."

You first patch the `package.json` to add a list of dependencies to ignore:

```json
{
  "scripts": {
    "shrinkwrapIgnore": "node ./shrinkwrapIgnore.js"
  },

  "shrinkwrapIgnore": [
    "fsevents"
  ],

  "devDependencies" {
    "jsonfile": "^2.4.0",
  }
}
```

And then you write a `shrinkwrapIgnore.js` file looking like:

```js
const _ = require('lodash');
const path = require('path');
const jsonfile = require('jsonfile');
const childProcess = require('child_process');
const shrinkwrapIgnore = require('./package.json').shrinkwrapIgnore;

const SHRINKWRAP_PATH = path.join(__dirname, 'npm-shrinkwrap.json');

try {
  childProcess.execSync('npm shrinkwrap --dev', {
    cwd: path.dirname(SHRINKWRAP_PATH)
  });
} catch (error) {
  console.error(error.stderr.toString());
  process.exit(1);
}

const shrinkwrapContents = jsonfile.readFileSync(SHRINKWRAP_PATH);
shrinkwrapContents.dependencies = _.omit(shrinkwrapContents.dependencies, shrinkwrapIgnore);
jsonfile.writeFileSync(SHRINKWRAP_PATH, shrinkwrapContents, {
  spaces: 2
});
```

## And then ...

Satisfied, you tell your team mate: "It's fixed!, just checkout the
`hack-for-windows` branch and ..."

{{< audio "it-was-at-this-moment.mp3" >}}

Yup, how is he going to run *any* `npm` stuff if `npm install` fails?

## Python to the rescue!

That's when a third team mate comes to the rescue. "Don't worry", he says,
"I'll rewrite your script in Python".

And that's what he comes up with:

```python
import sys
import collections
import json

with open("package.json", "r") as fp:
    package_json = json.load(fp)

to_remove = package_json["shrinkwrapIgnore"]

with open("npm-shrinkwrap.json", "r") as fp:
    shrinkwrap = json.load(fp, object_pairs_hook=collections.OrderedDict)

for dep in to_remove:
    print(sys.argv[0] + ":" ,"removing", dep)
    # do not fail if key is already removed:
    shrinkwrap["dependencies"].pop(dep, None)

with open("npm-shrinkwrap.json", "w") as fp:
    json.dump(shrinkwrap, fp, indent=2)

```

## Few notes


1/ Loading a value from a `.json` config file in Python is quite long:

```python
with open("foo.json", "w") as fp:
  data = json.load(fp)
  value = data["value"]
```

In `javascript`, it's a one-liner:

```js
const value = require("./foo.json").value
```

2/ We are using a small hack to make sure the order of the keys is preserved:

```python
import collections
import json

shrinkwrap = json.load(fp, object_pairs_hook=collections.OrderedDict)
```

This makes it possible to have a meaningful `diff` after we've run the Python
script. (Hopefully this will no longer be necessary starting with Python 3.6)


3/ Note how we use the `pop()` method with an `default` argument:

```python
my_dict.pop(key, None)
```

This is shorter and more readable than:

```python
if key in my_dict:
    del my_dict[key]
```

That's all for today, see you later!


[^1]: I _do_ think it is a good idea, but that's an other story ...
