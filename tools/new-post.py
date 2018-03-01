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
    subprocess.call(["nvim", post_path])


if __name__ == "__main__":
    main()
