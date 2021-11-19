import os
from typing import List, Tuple, Union, Optional, Type

from .pages import Page
from .util import join_path
from .writer import FileWriter


class Site:

    def __init__(self):
        self._pages = dict()
        self._files: Optional[List[dict]] = None

    def add_page(self, *page: Page, path: Optional[str] = None):
        for page in page:
            if not page.slug:
                raise ValueError(f"Can not add page without a slug: {page}")

            if path is not None:
                key = f"{path}/{page.slug}"
            else:
                key = page.slug

            if key in self._pages:
                raise ValueError(f"Trying to add page with existing path and slug '{key}'")

            self._pages[key] = {
                "path": path,
                "page": page,
            }

        self._files = None

    @property
    def associated_files(self) -> List[dict]:
        if self._files is None:
            self._files = []
            for p in self._pages.values():
                path: str = p["path"]
                page: Page = p["page"]
                for file in page.associated_files:
                    file_path = file["path"]
                    if not file["external"]:
                        file_path = join_path(path, file_path)

                    self._files.append({
                        "type": file["type"],
                        "external": file["external"],
                        "path": file_path,
                    })

        return self._files

    def write_files(
            self,
            root: Union[str, os.PathLike],
            format: str,
            writer: Optional[Type[FileWriter]] = None,
    ) -> FileWriter:
        assert format in ("md", "html")

        if writer is None:
            writer = FileWriter(root)
        else:
            writer = writer(root)

        for p in self._pages.values():
            page = p["page"]
            path = p["path"]
            if not page.slug:
                raise ValueError(f"Slug required for {page}")

            filename = join_path(path, f"{page.slug}.{format}")
            content = getattr(page, f"to_{format}")()

            writer.write(filename, content)

        return writer
