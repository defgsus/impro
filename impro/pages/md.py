import json
import html
from typing import Tuple, Optional, Dict

from marko import Markdown, Renderer, HTMLRenderer, inline


def get_markdown_elements(element) -> dict:
    r = ElementRenderer()
    r.render(element)
    return {
        "links": sorted(r.links),
        "headings": r.headings,
        "images": r.images,
    }


def replace_markdown_element_links(element, link_mapping: Dict[str, str]):
    if getattr(element, "dest", None) in link_mapping:
        element.dest = link_mapping[element.dest]

    if getattr(element, "children", None) and not isinstance(element, inline.RawText):
        for children in element.children:
            replace_markdown_element_links(children, link_mapping)


def replace_markdown_links(markdown: str, mapping: dict) -> str:
    # TODO: Should actually use marko to rerender the markdown
    for key, value in mapping.items():
        markdown = markdown.replace(f"({key})", f"({value})")
    return markdown


class ElementRenderer(HTMLRenderer):

    def __init__(self):
        super().__init__()
        self.links = set()
        self.headings = []
        self.images = []

    def render_heading(self, element):
        self.headings.append({
            "level": element.level,
            "text": self.render_children(element),
        })
        return super().render_heading(element)

    def render_link(self, element):
        self.links.add(element.dest)
        return super().render_link(element)

    def render_image(self, element):
        self.images.append({"title": self.render_children(element), "src": element.dest})
        return super().render_image(element)
