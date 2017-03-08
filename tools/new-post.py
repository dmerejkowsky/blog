import os
import re
import subprocess
import sys

import arrow

TEMPLATE="""\
---
slug: {slug}
date: {full_date}
draft: false
title: {title}
summary: |

---


<!--more-->
"""


def slugify(text):
    res = re.sub('[^\w\s-]', '', text).strip().lower()
    return re.sub('[-\s]+', '-', res)


def main():
    title = sys.argv[1]
    slug = slugify(title)
    now = arrow.get()
    file_name = now.strftime("%Y-%m-%d") + "-" + slug + ".md"
    full_date = arrow.get().isoformat()
    post_path = os.path.join("content/post", file_name)
    to_write = TEMPLATE.format(**locals())
    with open(post_path, "w") as fp:
        fp.write(to_write)
    to_run = [
        ("git" , "add", post_path),
        ("nvim", post_path),
    ]
    for cmd in to_run:
        subprocess.check_call(cmd)


if __name__ == "__main__":
    main()
