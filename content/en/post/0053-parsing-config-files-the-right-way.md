---
authors: [dmerej]
slug: parsing-config-files-the-right-way
date: "2017-09-09T10:54:46.595128+00:00"
draft: false
title: Parsing Config Files The Right Way
tags: ['python']
---

Parsing configuration files is something we programmers do everyday.
But are you sure you're doing it the proper way?

Let's find out!

<!--more-->

In the rest of this article, we'll assume we want to parse a configuration
file containing a github access token in a command line program called
`frob`.

# In Javascript

You may write something like this:

```javascript
/* in config.json */
{
  "auth":
  {
    "github":
    {
      "token": "ab642ef9zf"
    }
  }
}
```

```javascript
/* in frob.js */
const config = require('./config');
const token = config.auth.github.token;
...
```

Well, that's assuming we are using `node`. Making this work in a browser or in any other Javascript context is left as an exercise to the reader :)

There are several issues with the above approach, though. To explain them, we are going to switch to a language I know a lot better and see a list of problems and potential solutions.

# Syntax

First, using `JSON` for configuration files may not be such a good idea. So we're going to use YAML instead. Here are a few reasons why:

* Like JSON, we can map directly to "plain old data" Python types (lists, dictionaries, integers, floats, strings and booleans)

* Syntax is well-defined and all implementations behave the same. (It's _not_ the case for JSON, see [Parsing JSON is a Minefield](http://seriot.ch/parsing_json.php) for the details)

* We can have comments in the configuration file.

* File is easier to read for humans. Compare:

```json
{
  "auth":
  {
    "github":
    {
      "token": "ab642ef9zf"
    }
  }
}
```

```yaml
auth:
  github:
    token:  "ab642ef9zf"
```

* Elements can be arbitrary nested. (`.ini`  files only have one level of "sections", and `.toml` only two)

* There are several ways to express the same data, so we can choose whatever is the more readable:

```yaml
shopping_list:
 - eggs
 - bacon
 - tomatoes
 - beans

tags: ["python", "testing"]
```

* Whitespace is significant, so the file *has* to be properly indented.


# Location

Second, the `config.json` file is hard-coded to be located right next to the source code.

This means it's possible it will get added and pushed into a version control system if we are not careful.

So instead we'll try to be compatible with [freedesktop standards](https://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html).

Basically this means we should:

* Look for config file in `$XDG_CONFIG_HOME/frob.yml` if XDG_CONFIG_HOME environment variable is set.
* If not, look for it in `~/.config/frob.yml`
* And if not found in the home, look for the default in `/etc/xdg/frob.yml`

Doing so will help us follow the [principle of least astonishment](https://en.wikipedia.org/wiki/Principle_of_least_astonishment) because, since many programs follow those rules today, users of our implementation will *expect* us to do the same.

Fortunately, we don't have to implement all of this, we can use the `pyxdg` library:

```python
import xdg.BaseDirectory

cfg_path = xdg.BaseDirectory.load_first_config("frob.yml")
if cfg_path:
   ...
```

# Error handling

Sometimes the file won't exist at all, so we'll want to inform our user about that:

```python
cfg_path = xdg.BaseDirectory.load_first_config("frob.yml")

if not cfg_path:
    raise InvalidConfig("frob.yml not found")
```

Sometimes the file will exist but `read_text()` will fail for some reason (like a permission issue):

```python
import pathlib

try:
   config_file = pathlib.Path(cfg_path)
   contents = config_file.read_text()
except OSError as read_error:
    raise InvalidConfig(f"Could not read file {cfg_path}: {read_error}")
```


Sometimes the file will exist but will contain invalid YAML:

```python
import ruamel.yaml

contents = config_file.read_text()
try:
    parsed = ruamel.yaml.safe_load(contents)
except ruamel.yaml.error.YAMLError as yaml_error:
    details = format_error(yaml_error.context_mark.line, yaml_error.context_mark.column)
    message = f"{cfg_path}: YAML error: {details}"
    raise InvalidConfig(message)
```

# Schema

That's where things get tricky. What if the file exists, is readable, contains valid YAML code but the user made a typo when writing it?

Here's a few cases we should handle:

```yaml
# empty config: no error

# `auth` section is here but does not contain
# a `github` entry: no error
auth:
  gitlab:
    ...

# `auth.github` section is here but does not
# contain `token`, this is an error:
auth:
  github:
    tken: "ab642ef9zf"
```

A naive way to handle this would be to write code like this:

```python
parsed = ruamel.yaml.safe_load(contents)
auth = parsed.get("auth")
if auth:
    github = auth.get("github")
    token = github.get("token")
    if not token:
        raise InvalidConfig("Expecting a key named 'token' in the
                            'github' section of 'auth' config")
```

This gets tedious very quickly. A better way is to use the `schema` library:

```python
import schema
auth_schema = schema.Schema(
  {
    schema.Optional("auth"):
    {
      schema.Optional("github") :
      {
        "token": str,
      }
    }
  }
)

try:
    auth_schema.validate(parsed)
except schema.SchemaError as schema_error:
    raise InvalidConfig(file_path, schema_error)
```

# Saving

Last but not least, sometimes we'll want to automatically save the configuration file.

In that case, it's important that the saved configuration file still resembles the original one.

With `ruamel.yaml`, this is done by using a `RoundtripLoader`

```python
def save_token(token):
    contents = config_file.read_text()
    config = ruamel.yaml.load(contents, ruamel.yaml.RoundTripLoader)
    config["auth"]["github"]["token"] = token
    dumped = ruamel.yaml.dump(config, Dumper=ruamel.yaml.RoundTripDumper)
    config_file.write_text(dumped)
```

# Conclusion

Phew! That was a lot of work for a seemingly easy task. But I do believe it's worth going through all this trouble: we covered a lot of edge cases and made sure we had always very clear error messages raised. Users of code written like this will be very grateful when things go south. Cheers!
