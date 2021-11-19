import json
import html
from typing import Tuple, Optional

from marko import Markdown, Renderer, HTMLRenderer


def get_markdown_elements(doc) -> dict:
    r = ElementRenderer()
    r.render(doc)
    return {
        "links": sorted(r.links),
        "headings": r.headings,
        "images": r.images,
    }


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
