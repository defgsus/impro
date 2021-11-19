import unittest
from pathlib import Path

from impro.pages import Page


DATA_PATH = Path(__file__).resolve().parent / "data"


class TestPages(unittest.TestCase):

    def assertElements(self, page: Page, name: str, expected_elements: list):
        elements = page.elements
        if name not in elements:
            raise AssertionError(f"'{name}' not in elements for {page}, got {elements}")

        self.assertEqual(
            expected_elements, elements[name],
            f"for {page}"
        )

    def test_no_front_matter(self):
        page = Page.from_file(DATA_PATH / "no_front_matter.md")
        self.assertEqual("headline 1", page.title)
        self.assertEqual("no-front-matter", page.slug)
        self.assertElements(page, "links", ["#headline-1", "https://targ.et"])
        self.assertElements(page, "headings", [{"level": 1, "text": "headline 1"}, {"level": 2, "text": "headline 2"}])

    def test_front_matter(self):
        page = Page.from_file(DATA_PATH / "front_matter.md")
        self.assertEqual("The Title", page.title)
        self.assertEqual("the-slug", page.slug)
        self.assertElements(page, "links", ["#headline-1", "https://targ.et"])
        self.assertElements(page, "headings", [{"level": 1, "text": "headline 1"}, {"level": 2, "text": "headline 2"}])

    def test_extending_no_front_matter(self):
        page = Page.from_file(DATA_PATH / "sub_no_fm.md")
        self.assertEqual("--  --", page.title)  # TODO: should actually be empty?
        self.assertEqual("sub-no-fm", page.slug)
        self.assertElements(page, "links", ["https://targ.et/.html"]) # TODO: it's missing the slug
        self.assertElements(page, "headings", [{"level": 1, "text": "--  --"}])
        self.assertEqual(
            """# --  --
(this is base.md)

This Is Sub!

---
(this is base.md again)
[self-link](https://targ.et/.html)
""",
            page.to_md()
        )

    def test_extending_with_front_matter(self):
        page = Page.from_file(DATA_PATH / "sub_fm.md")
        self.assertEqual("SubGenius", page.title)  # TODO: should actually be '-- SubGenius --' ?
        self.assertEqual("sub-fm", page.slug)
        self.assertElements(page, "links", ["https://targ.et/.html"]) # TODO: it's missing the slug
        self.assertElements(page, "headings", [{"level": 1, "text": "-- SubGenius --"}])
        self.assertEqual(
            """# -- SubGenius --
(this is base.md)

This Is Sub!

---
(this is base.md again)
[self-link](https://targ.et/.html)
""",
            page.to_md()
        )

    def test_images_no_front_matter(self):
        page = Page.from_file(DATA_PATH / "images_no_fm.md")
        self.assertEqual("", page.title)
        self.assertEqual("images-no-fm", page.slug)
        self.assertElements(page, "images", [
            {"title": "image 1", "src": "image1.png"},
            {"title": "image 2", "src": "sub-path/image2.png"}
        ])

        self.assertEqual(
            """![image 1](image1.png)

Here is ![image 2](sub-path/image2.png).
""",
            page.to_md()
        )
