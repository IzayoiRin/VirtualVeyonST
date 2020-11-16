import sys
import os
import re

SUBS = [
    "../stmanager.py",
    "logs/.readme", "servers/__init__.py", "tasks/__init__.py",
    "__init__.py", "settings.py", "requirements.devel"
]
FILE = re.compile(r"^([a-z0-9A-Z_]*)\.[a-z0-9A-Z_]+$")
TEMPLATES = {
    "stmanager": ["manager.temp", r"Application"],
    "requirements": "requirements.temp",
    "settings": "settings.temp"
}


def create(dirpath: str, father: str, render: callable):
    temp = dirpath.split("/", 1)
    if not temp[0]:
        return
    cur = os.path.join(father, temp[0])
    match = re.match(FILE, temp[0])
    if match:
        print("make file: %s" % cur)
        with open(cur, "w") as f:
            template = TEMPLATES.get(match.group(1))
            if template and callable(render):
                f.write(render(template))
    elif not os.path.exists(cur):
        print("make dir: %s" % cur)
        os.makedirs(cur)
    if len(temp) > 1:
        create(temp[1], cur, render)


def render(father, **renderdict):
    def inner(template):
        if isinstance(template, list):
            template, flag = template
            with open(os.path.join(father, template), "r") as f:
                return re.sub(r"\{\{%s\}\}" % flag, renderdict[flag], f.read())
        with open(os.path.join(father, template), "r") as f:
            return f.read()
    return inner


def main():
    try:
        file, name = sys.argv
    except ValueError as e:
        print("Illegal command parameters, %s" % e)
        return
    app = os.path.join(os.getcwd(), name)
    if os.path.exists(app):
        print("Target application direct has been EXISTED, %s" % app)
        return
    print("Start application at: %s" % app)
    templates = os.path.join(os.path.split(file)[0], "templates")
    # os.makedirs(app)
    for sub in SUBS:
        create(sub, app, render(templates, Application=name))


if __name__ == '__main__':
    main()
