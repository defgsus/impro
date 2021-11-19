from pathlib import Path
from typing import List, Union, Optional, TextIO, Dict

from ..environment import Environment
from ..util import sluggify, join_path
from .markup import Markup
from .md import replace_markdown_links


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
            file: Union[str, Path, TextIO],
            env: Optional[Environment] = None,
    ) -> "Page":
        return cls.from_file(file, format="md", env=env)

    @classmethod
    def from_file(
            cls,
            file: Union[str, Path, TextIO],
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
            self._get_associated_files()

        return self._files

    def css_files(self) -> List[str]:
        css = self.markup.get_front_matter_value("css")
        if not css:
            return []
        if isinstance(css, str):
            css = [css]
        return css

    def _get_associated_files(self):
        root_path = "/"
        if self.markup.filename:
            root_path = self.markup.filename.resolve().parent

        handled_path_set = set()

        def _add_file(file_type, path):
            external = "//" in path
            if external:
                abs_path = path
            else:
                abs_path = join_path(root_path, path)

            if abs_path in handled_path_set:
                return

            handled_path_set.add(abs_path)

            self._files.append({
                "type": file_type,
                "external": external,
                "path": path,
                "abs_path": abs_path,
            })

        if self.elements.get("images"):
            for i in self.elements["images"]:
                _add_file("image", i["src"])

        for file in self.css_files():
            _add_file("css", file)

    def to_md(self, link_mapping: Optional[Dict[str, str]] = None) -> str:
        if self.markup.format == "md":
            markup = self.markup.markup(self.context, env=self.env)
            if link_mapping:
                markup = replace_markdown_links(markup, link_mapping)
            return markup
        else:
            raise NotImplementedError(self.markup.format)

    def to_html(self, link_mapping: Optional[Dict[str, str]] = None) -> str:
        if self.markup.format == "md":
            html_body = self.markup.to_html(self.context, self.env, link_mapping=link_mapping)
            layout = self.layout("html")
            if not layout:
                return html_body

            markup = Markup.from_file(layout, format="html", env=self.env)
            context = self.context.copy()
            context.setdefault("html", {})
            context["html"].setdefault("body", html_body)
            context["html"].setdefault("title", self.title)
            context.setdefault("slug", self.slug)
            if not context["html"].get("css"):
                context["html"]["css"] = []
            for file in self.css_files():
                if link_mapping:
                    file = link_mapping.get(file, file)
                context["html"]["css"].append(file)

            return markup.to_html(context=context, env=self.env, link_mapping=link_mapping)
        else:
            raise NotImplementedError(self.markup.format)
