from typing import Tuple, Optional
from yaml import safe_load
from yaml.scanner import ScannerError


from ..excpetions import FrontMatterError


def split_front_matter_and_markup(markup: str) -> Tuple[Optional[dict], str]:
    """
    Split a text into it's front-matter and markup

    :return: tuple of (dict|None, str)
    """
    markup_lines = markup.strip().splitlines()
    if len(markup_lines) < 4:
        return None, "\n".join(markup_lines) + "\n"

    if markup_lines[0].strip() != "---":
        return None, "\n".join(markup_lines) + "\n"

    fm_lines = []
    markup_lines.pop(0)
    while markup_lines and markup_lines[0] != "---":
        fm_lines.append(markup_lines.pop(0))

    if not markup_lines:
        return None, "\n".join(markup_lines) + "\n"

    returned_markup = "\n".join(markup_lines[1:]) + "\n"
    front_matter = "\n".join(fm_lines) + "\n"

    try:
        front_matter = safe_load(front_matter)
    except ScannerError as e:
        raise FrontMatterError(f"Parsing front-matter failed: {e}")

    if isinstance(front_matter, str):
        raise FrontMatterError("Parsing front-matter failed")

    return front_matter, returned_markup
