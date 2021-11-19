import unittest
from pathlib import Path

from impro.pages import Page


DATA_PATH = Path(__file__).resolve().parent / "data"


class TestPages(unittest.TestCase):

    def test_no_front_matter(self):
        page = Page.from_file(DATA_PATH / "no_front_matter.md")
        self.assertEqual("headline 1", page.title)
        self.assertEqual("no-front-matter", page.slug)
        self.assertEqual(
            {
                "links": ["#headline-1", "https://targ.et"],
                "headings": [{"level": 1, "text": "headline 1"}, {"level": 2, "text": "headline 2"}]
            },
            page.elements
        )

    def test_front_matter(self):
        page = Page.from_file(DATA_PATH / "front_matter.md")
        self.assertEqual("The Title", page.title)
        self.assertEqual("the-slug", page.slug)
        self.assertEqual(
            {
                "links": ["#headline-1", "https://targ.et"],
                "headings": [{"level": 1, "text": "headline 1"}, {"level": 2, "text": "headline 2"}]
            },
            page.elements
        )

    def test_extending_no_front_matter(self):
        page = Page.from_file(DATA_PATH / "sub_no_front_matter.md")
        self.assertEqual("--  --", page.title)  # TODO: should actually be empty?
        self.assertEqual("sub-no-front-matter", page.slug)
        self.assertEqual(
            {
                "links": ["https://targ.et/.html"],
                "headings": [{"level": 1, "text": "--  --"}]
            },
            page.elements
        )
        self.assertEqual(
            """# --  --
(this is base.md)

This Is Sub!

---
(this is base.md again)
[self-link](https://targ.et/.html)""",
            page.to_md()
        )

    def test_extending_with_front_matter(self):
        page = Page.from_file(DATA_PATH / "sub_front_matter.md")
        self.assertEqual("SubGenius", page.title)  # TODO: should actually be '-- SubGenius --' ?
        self.assertEqual("sub-front-matter", page.slug)
        self.assertEqual(
            {
                "links": ["https://targ.et/.html"],
                "headings": [{"level": 1, "text": "-- SubGenius --"}]
            },
            page.elements
        )
        self.assertEqual(
            """# -- SubGenius --
(this is base.md)

This Is Sub!

---
(this is base.md again)
[self-link](https://targ.et/.html)""",
            page.to_md()
        )
