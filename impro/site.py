import os
from pathlib import Path
from typing import List, Tuple, Union, Optional, Type, Generator

from .pages import Page
from .util import join_path, relative_path
from .writer import FileWriter


class Site:

    def __init__(self):
        self._pages = dict()
        self._files: Optional[List[dict]] = None
        self.file_type_path_mapping = {
        #    "image": "images",
        }

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
            root: Union[str, Path],
            format: str,
            writer: Optional[Type[FileWriter]] = None,
    ) -> FileWriter:
        if writer is None:
            writer = FileWriter(root=root)
        else:
            writer = writer(root=root)

        for filename, content in self.iter_files(format=format):
            writer.write(filename, content)

        return writer

    def iter_files(
            self,
            format: str,
    ) -> Generator[Tuple[Path, Union[str, bytes]], None, None]:
        assert format in ("md", "html")

        handled_path_set = set()

        for p in self._pages.values():
            page = p["page"]
            page_path = p["path"]
            if not page.slug:
                raise ValueError(f"Slug required for {page}")

            page_link_mapping = dict()

            for file in page.associated_files:
                if not file["external"]:
                    real_file_path = Path(file["abs_path"])
                    file_path = file["path"]

                    if file["type"] in self.file_type_path_mapping:
                        export_file_path = join_path(self.file_type_path_mapping[file["type"]], file_path)
                    else:
                        export_file_path = join_path(page_path, file_path)
                    export_file_path = relative_path(export_file_path, page_path)

                    if file_path != export_file_path:
                        page_link_mapping[file_path] = export_file_path

                    if real_file_path not in handled_path_set:
                        handled_path_set.add(real_file_path)

                        if not real_file_path.exists():
                            raise IOError(
                                f"Associated file '{real_file_path}' does not exist for '{page}'"
                            )

                        with open(real_file_path, "rb") as fp:
                            yield Path(export_file_path), fp.read()

            filename = f"{page.slug}.{format}"
            if page_path:
                filename = join_path(page_path, filename)

            content = getattr(page, f"to_{format}")(link_mapping=page_link_mapping)

            yield Path(filename), content


