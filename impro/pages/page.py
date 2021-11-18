import os
from pathlib import Path
from typing import List, Tuple, Union, Optional, TextIO

from jinja2 import Template

from .frontmatter import split_front_matter_and_markup
from .formats import get_filename_format
from ..environment import Environment
from .markup import Markup


class Page:

    def __init__(
            self,
            markup: Markup,
            env: Optional[Environment] = None,
    ):
        self.markup = markup
        self._env = None
        self._env_default = env

        self.context = dict()
        if self.markup.front_matter:
            if self.markup.front_matter.get("title"):
                self.context["title"] = self.markup.front_matter["title"]

            if self.markup.front_matter.get("context"):
                ctx = self.markup.front_matter["context"]
                if not isinstance(ctx, dict):
                    raise TypeError(f"front-matter 'context' must be of type dict, got '{type(ctx).__name__}'")
                self.context.update(ctx)

    @classmethod
    def from_markdown(
            cls,
            file: Union[str, os.PathLike, TextIO],
            env: Optional[Environment] = None,
    ) -> "Page":
        markup = Markup.from_markdown(file, env=env)
        return Page(markup, env=env)

    @classmethod
    def from_file(
            cls,
            file: Union[str, os.PathLike, TextIO],
            format: Optional[str] = None,
            env: Optional[Environment] = None,
    ) -> "Page":
        markup = Markup.from_file(file, format=format, env=env)
        return Page(markup, env=env)

    @property
    def env(self):
        if not self._env:
            if self._env_default:
                self._env = self._env_default.copy()
            else:
                self._env = Environment()

            if self.markup.filename:
                self._env.add_search_path(self.markup.filename.parent, front=True)

            # TODO: update from front-matter

        return self._env

    def to_html(self) -> str:
        return self.markup.to_html(self.context, self.env)
