import unittest

from impro.pages.frontmatter import split_front_matter_and_markup
from impro.excpetions import FrontMatterError


class TestFrontmatter(unittest.TestCase):

    def test_split(self):
        text = """
---
a:
  b: 2
---
# Document
"""
        self.assertEqual(
            (
                {"a": {"b": 2}},
                "# Document\n"
            ),
            split_front_matter_and_markup(text)
        )

    def test_none(self):
        self.assertEqual(
            (None, "# Document\n"),
            split_front_matter_and_markup("""# Document""")
        )

        self.assertEqual(
            (None, "---\n# Document\n"),
            split_front_matter_and_markup("""---\n# Document""")
        )

        self.assertEqual(
            (None, "---\na: 2\n# Document\n"),
            split_front_matter_and_markup("""---\na: 2\n# Document""")
        )

    def test_invalid_yaml(self):
        with self.assertRaises(FrontMatterError):
            split_front_matter_and_markup("""---\nblabla\n---\n# Document""")

        with self.assertRaises(FrontMatterError):
            split_front_matter_and_markup("""---\na:\n2\n---\n# Document""")
