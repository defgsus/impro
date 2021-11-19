import unittest
from pathlib import Path

from impro.util import join_path


class TestPaths(unittest.TestCase):

    def test_join_path(self):
        self.assertEqual(
            "docs/index.html",
            join_path("docs", "index.html")
        )
        self.assertEqual(
            "docs/index.html",
            join_path("docs", "./index.html")
        )
        self.assertEqual(
            "docs/index.html",
            join_path("docs/sub", "../index.html")
        )
