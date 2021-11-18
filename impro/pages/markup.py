import os
from pathlib import Path
from typing import List, Tuple, Union, Optional, TextIO

from .frontmatter import split_front_matter_and_markup
from .formats import get_filename_format
from ..environment import Environment


class Markup:

    def __init__(
            self,
            markup: str,
            format: str,
            front_matter: Optional[dict] = None,
            filename: Optional[Union[str, os.PathLike]] = None,
    ):
        self.markup_template = markup
        self._markup: Optional[str] = None
        self.format = format
        self.front_matter = front_matter
        self.filename: Optional[Path] = Path(filename) if filename is not None else None

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
        # read from stream
        if hasattr(file, "read"):
            if not format:
                raise ValueError(f"Need to specify 'format' when 'file' is a stream")
            text = file.read()
            filename = None

        # read from file
        else:
            if not format:
                format = get_filename_format(file)
                if not format:
                    raise ValueError(f"Need to specify 'format', it can not be guessed from filename '{file}'")
            filename = Path(file)
            text = filename.read_text()

        fm, markup = split_front_matter_and_markup(text)

        return cls(
            markup=markup,
            format=format,
            front_matter=fm,
            filename=filename,
        )

    def markup(self, context: Optional[dict] = None, env: Optional[Environment] = None) -> str:
        if self._markup is None:
            if "{%" not in self.markup_template and "{{" not in self.markup_template:
                self._markup = self.markup_template
            else:
                self._render_template(context=context, env=env)
        return self._markup

    def to_html(self, context: Optional[dict] = None, env: Optional[Environment] = None) -> str:
        from marko import Markdown
        from marko.html_renderer import HTMLRenderer
        assert self.format == "md"
        md = Markdown()
        doc = md.parse(self.markup(context=context, env=env))
        return HTMLRenderer().render(doc)

    def get_elements(self, context: Optional[dict] = None, env: Optional[Environment] = None) -> dict:
        from .md import Markdown, get_markdown_elements
        assert self.format == "md"
        md = Markdown()
        doc = md.parse(self.markup(context=context, env=env))
        return get_markdown_elements(doc)

    def _render_template(self, context: Optional[dict], env: Optional[Environment]):
        if context is None:
            context = dict()
        if env is None:
            env = Environment()

        template = env.jinja_env().from_string(
            source=self.markup_template,
        )
        self._markup = template.render(**context)
