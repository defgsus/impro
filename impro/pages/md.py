import json
import html
from typing import Tuple, Optional

from marko import Markdown, Renderer, HTMLRenderer

from .frontmatter import split_front_matter_and_markup

"""
def load_markdown(filename: str) -> Tuple[Optional[dict], str]:
    with open(filename) as fp:
        text = fp.read()

    return parse_markdown(text)


def parse_markdown(markdown: str) -> Tuple[Optional[dict], str]:
    fm, markdown = split_front_matter_and_markup(markdown)
    return fm, markdown
    #md = Markdown()
    #doc = md.parse(markdown)
    #print(doc.children)
    #print(json.dumps(ASTRenderer().render(doc), indent=2))
"""


def get_markdown_elements(doc) -> dict:
    r = ElementRenderer()
    r.render(doc)
    return {
        "links": sorted(r.links),
        "headings": r.headings,
    }


class ElementRenderer(HTMLRenderer):

    def __init__(self):
        super().__init__()
        self.links = set()
        self.headings = []

    def render_heading(self, element):
        self.headings.append({
            "level": element.level,
            "text": self.render_children(element),
        })
        return super().render_heading(element)

    def render_link(self, element):
        self.links.add(element.dest)
        return super().render_link(element)
