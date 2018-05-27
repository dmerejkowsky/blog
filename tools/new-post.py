import os
import pathlib
import re
import subprocess
import sys

import arrow


TEMPLATE = """\
---
authors: [dmerej]
slug: {slug}
date: {full_date}
draft: false
title: "{title}"
tags:
summary: |

---


<!--more-->
"""


def slugify(text):
    # Make sure 'C++ stuff" is replaced by 'cpp-stuff', not 'c-stuff'
    text = text.replace("C++", "cpp")
    res = re.sub('[^\w\s-]', '', text).strip().lower()
    return re.sub('[-\s]+', '-', res)


def get_last_index():
    this_path = pathlib.Path(".")
    all_posts = (this_path / "content/post").glob("*.md")

    def get_index(p):
        try:
            return int(p.name[:4])
        except ValueError:
            return 0

    latest = max(get_index(p) for p in all_posts)
    return latest


def main():
    title = sys.argv[1]
    slug = slugify(title)
    now = arrow.get()
    last_index = get_last_index()
    file_name = "%04i" % (last_index + 1) + "-" + slug + ".md"
    full_date = arrow.get().isoformat()
    post_path = os.path.join("content/post", file_name)
    to_write = TEMPLATE.format(**locals())
    with open(post_path, "w") as fp:
        fp.write(to_write)
    subprocess.call(["nvim", post_path])


if __name__ == "__main__":
    main()
