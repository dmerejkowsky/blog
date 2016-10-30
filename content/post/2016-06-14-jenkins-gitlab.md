+++
slug = "jenkins-gitlab"
date = "2016-06-14T19:38:03+02:00"
description = ""
draft = true
tags = []
title = "Connecting Jenkins to Gitlab"
topics = []

+++

This is *not* a tutorial, it's the story of how I managed to do it.
Hopefully at the end you'll learn a few things that will be useful
to you in the future.

Steps

* get gitlab docker image -> too easy
  (did not use docker-compose, just a bash script)

* get 'raw' jenkins.war : you just need java, no need for .deb or installer or
  docker image, it's overkill

* Installed gitlab plugin: talking about a 'webhook'

* Found 'webhook' from Gitlab, adding a hook on localhost:8080, clicking on 'test' -> 404
 * dafuck? It's a **gitlab** error page?

* Figured out it comes from docker ... You can reach the host from docker, but to do this
  you need netstat and some magic:

```bash
netstat -nr | grep '^0\.0\.0\.0' | awk '{print $2}'


# TODO: rewrite this with just awk :P

```

* OK, hook is created, but job is not triggered

* Trying with 'push events' -> it works

* Wrote a quick flask server to see what gitlab posts -> nothing when creating merge requests

```python

import pprint
import flask

app = flask.Flask(__name__)

@app.route("/project/hello", methods=["POST"])
def hello_proj():
    print("Recieved something on project/hello")
    pprint.pprint(flask.request.json)
    return "ok\n", 200

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=8080)

```

* Turned out I forgot to check the 'merge request events' when creating the webhook :P
