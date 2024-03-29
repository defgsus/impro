import unittest
from pathlib import Path

from impro.site import Site
from impro.pages import Page
from impro.writer import MemoryWriter

DATA_DIR = Path(__file__).resolve().parent / "data"


class TestSite(unittest.TestCase):

    def test_site_writer(self):
        site = Site()
        site.add_page(
            Page.from_file(DATA_DIR / "no_front_matter.md"),
            Page.from_file(DATA_DIR / "front_matter.md"),
        )
        writer = site.write_files("/", "md", writer=MemoryWriter)
        self.assertEqual(
            {
                Path('/no-front-matter.md'): '# headline 1\n\nparagraph\n\n## headline 2\n\nA [weblink](https://targ.et).\n\nLink to [headline one](#headline-1)\n',
                Path('/the-slug.md'): '# headline 1\n\nparagraph\n\n## headline 2\n\nA [weblink](https://targ.et).\n\nLink to [headline one](#headline-1)\n'
            },
            writer.files
        )
        writer = site.write_files("/docs", "md", writer=MemoryWriter)
        self.assertEqual(
            {
                Path('/docs/no-front-matter.md'): '# headline 1\n\nparagraph\n\n## headline 2\n\nA [weblink](https://targ.et).\n\nLink to [headline one](#headline-1)\n',
                Path('/docs/the-slug.md'): '# headline 1\n\nparagraph\n\n## headline 2\n\nA [weblink](https://targ.et).\n\nLink to [headline one](#headline-1)\n'
            },
            writer.files
        )

    def test_site_writer_assets(self):
        site = Site()
        site.add_page(
            Page.from_file(DATA_DIR / "images_no_fm.md"),
            Page.from_file(DATA_DIR / "with_css.md"),
        )
        writer = site.write_files("/", "md", writer=MemoryWriter)
        filenames = set(str(f) for f in writer.files.keys())
        self.assertEqual(
            {"/images-no-fm.md", "/with-css.md", "/style.css",
             "/image1.png", "/sub-path/image2.png"},
            filenames,
        )
