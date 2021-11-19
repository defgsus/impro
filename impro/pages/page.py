import os
from typing import List, Union, Optional, TextIO

from ..environment import Environment
from .markup import Markup
from impro.util import sluggify


class Page:

    def __init__(
            self,
            markup: Markup,
            env: Optional[Environment] = None,
    ):
        self.markup = markup
        self._elements = None
        self._files = None
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

    def __str__(self):
        return f"Page({self.markup.filename})"

    @property
    def title(self) -> str:
        highest_heading = (100, "")
        for heading in self.elements["headings"]:
            if heading["level"] < highest_heading[0]:
                highest_heading = (heading["level"], heading["text"])

        return self.markup.get_front_matter_value("title", highest_heading[1]) or ""

    @property
    def slug(self) -> str:
        slug = None
        if self.markup.filename:
            slug = self.markup.filename.name
            if "." in slug:
                slug = ".".join(slug.split(".")[:-1])
            slug = sluggify(slug)

        return self.markup.get_front_matter_value("slug", slug) or ""

    def layout(self, format: str) -> Optional[str]:
        """
        The configured layout for the output format.

        :param format: str, desired output format
        :return: either None or a template filename
        """
        if format == "html":
            layout = self.env.html_default_layout
        elif format == "md":
            layout = None
        else:
            raise NotImplementedError(format)

        return self.markup.get_front_matter_value("layout", layout)

    @classmethod
    def from_markdown(
            cls,
            file: Union[str, os.PathLike, TextIO],
            env: Optional[Environment] = None,
    ) -> "Page":
        return cls.from_file(file, format="md", env=env)

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
                self._env.add_search_path(self.markup.filename.parent)

            # TODO: update from front-matter

        return self._env

    @property
    def elements(self) -> dict:
        if self._elements is None:
            self._elements = self.markup.get_elements(self.context, self.env)
        return self._elements

    @property
    def associated_files(self) -> List[dict]:
        if self._files is None:
            self._files = []
            if self.elements.get("images"):
                for i in self.elements["images"]:
                    self._files.append({
                        "type": "image",
                        "external": "//" in i["src"],
                        "path": i["src"],
                    })
        return self._files

    def to_md(self) -> str:
        if self.markup.format == "md":
            return self.markup.markup(self.context, self.env)
        else:
            raise NotImplementedError(self.markup.format)

    def to_html(self) -> str:
        if self.markup.format == "md":
            html_body = self.markup.to_html(self.context, self.env)
            layout = self.layout("html")
            if not layout:
                return html_body

            markup = Markup.from_file(layout, format="html", env=self.env)
            context = self.context.copy()
            context.setdefault("html", {})
            context["html"].setdefault("body", html_body)
            context["html"].setdefault("title", self.title)
            context.setdefault("slug", self.slug)

            return markup.to_html(context=context, env=self.env)
        else:
            raise NotImplementedError(self.markup.format)
