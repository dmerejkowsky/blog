import sqlite3
import re
import arrow

connection = sqlite3.connect("/home/dmerej/backups/dmerej.info/blog/db/blog-2016-05-21.sqlite")

cursor = connection.cursor()

def slugify(text):
    res = re.sub('[^\w\s-]', '', text).strip().lower()
    return re.sub('[-\s]+', '-', res)

for title, contents, dc_date in cursor.execute("""\
SELECT
    post_title, post_content, post_creadt
FROM dc_post
WHERE post_type == "post"
"""
):
    iso_date = arrow.get(dc_date).isoformat()
    slug = slugify(title)
    path = "content/post/%s.md" % slug
    with open(path, "w") as fp:
        fp.write("""\
+++
date = "{date}"
draft = false
title = "{title}"
+++

""".format(date=iso_date, title=title))

    if not contents.endswith("\n"):
        contents += "\n"
    with open(path, "a") as fp:
        fp.write(contents)
    print("Imported", path)
