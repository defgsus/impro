import os
from pathlib import Path
from typing import List, Tuple, Union, Optional, Iterable

from jinja2 import Environment as JinjaEnvironment
from jinja2 import Template, FileSystemLoader


class Environment:

    IMPRO_PATH: Path = Path(__file__).parent

    def __init__(
            self,
            search_paths: Optional[Iterable[Union[str, os.PathLike]]] = None,
            html_default_layout: str = "base.html",
    ):
        self.html_default_layout = html_default_layout

        self._search_paths: List[Path] = []
        if search_paths is not None:
            self._search_paths = [Path(p) for p in search_paths]
        self._search_paths.append(self.IMPRO_PATH / "templates")

        self._jinja_env: Optional[JinjaEnvironment] = None

    def __copy__(self):
        e = Environment()
        e._search_paths = self._search_paths.copy()
        return e

    def copy(self) -> "Environment":
        return self.__copy__()

    @property
    def search_paths(self) -> List[Path]:
        return self._search_paths

    def add_search_path(self, *path: Union[str, os.PathLike], back: bool = False):
        if back:
            for p in reversed(path):
                self._search_paths.append(Path(p))
        else:
            for p in path:
                self._search_paths.insert(0, Path(p))
        self._jinja_env = None

    @search_paths.setter
    def search_paths(self, paths: List[Path]):
        self._search_paths = paths.copy()
        self._jinja_env = None

    def find_file(self, file: Union[str, Path]) -> Optional[Path]:
        file = Path(file)
        if file.is_absolute():
            return file if file.exists() else None

        for p in self.search_paths:
            pf = p / file
            if pf.exists():
                return pf

    def jinja_env(self) -> JinjaEnvironment:
        if self._jinja_env is None:
            self._jinja_env = JinjaEnvironment(
                loader=FileSystemLoader(searchpath=self._search_paths)
            )
        return self._jinja_env

