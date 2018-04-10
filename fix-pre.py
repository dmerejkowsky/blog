import sys

with open(sys.argv[1], "r") as f:
    lines = f.readlines()

new_lines = list()
for line in lines:
    if line == "<pre>\n":
        new_line = "```\n"
    elif line == "```text\n":
        new_line = "```\n"
    elif line == "```console\n":
        new_line = "```\n"
    elif line == "</pre>\n":
        new_line = "```\n"
    else:
        new_line = line
    new_lines.append(new_line)

with open(sys.argv[1], "w") as f:
    f.writelines(new_lines)
