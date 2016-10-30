import path
import re

def get_date(post_path):
    text = post_path.text()
    for line in text.splitlines():
        match = re.match(r"^date.*(\d{4}-\d{2}-\d{2}).*", line)
        if match:
            return match.groups()[0]
    else:
        print("No date for", post_path)

for post_path in path.Path("content/post").files("*.md"):
    date = get_date(post_path)
    slug = post_path.namebase
    contents = post_path.text()
    lines = contents.splitlines()
    lines.insert(1, "slug = %s\n" % slug)
    new_path = post_path.dirname().joinpath("%s-%s.md" % (date, slug))
    new_path.write_lines(lines)
    print("Written", new_path)
