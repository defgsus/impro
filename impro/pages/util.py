

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


