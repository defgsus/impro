import urllib.parse


def sluggify(s: str) -> str:
    r = ""
    for c in s:
        add_c = c
        if c.isspace():
            add_c = "-"

        elif not c.isalnum():
            add_c = "-"

        if add_c == "-":
            if not r.endswith("-"):
                r += add_c
        else:
            r += add_c

    return r


def join_path(*paths: str) -> str:
    if len(paths) == 0:
        return ""
    elif len(paths) == 1:
        return paths[1]
    elif len(paths) > 2:
        return join_path(join_path(paths[0], paths[1]), *paths[2:])

    root = paths[0]
    if root and not root.endswith("/"):
        root = root + "/"
    return urllib.parse.urljoin(root, paths[1])
