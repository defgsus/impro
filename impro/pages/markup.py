import os
from io import StringIO
from pathlib import Path
from typing import List, Tuple, Union, Optional, TextIO, Type

from .frontmatter import split_front_matter_and_markup
from .formats import get_filename_format
from ..environment import Environment


class Markup:

    def __init__(
            self,
            markup: str,
            format: str,
            front_matter: Optional[dict] = None,
            filename: Optional[Union[str, Path]] = None,
    ):
        self.markup_template = markup
        self._markup: Optional[str] = None
        self.format = format
        self.front_matter = front_matter
        self.filename: Optional[Path] = Path(filename) if filename is not None else None

    @classmethod
    def from_markdown(
            cls,
            file: Union[str, Path, TextIO],
            env: Optional[Environment] = None,
    ) -> "Markup":
        return cls.from_file(file, format="md", env=env)

    @classmethod
    def from_string(
            cls,
            markup: str,
            format: Optional[str] = None,
            env: Optional[Environment] = None,
    ) -> "Markup":
        fp = StringIO(markup)
        return cls.from_file(fp, format=format, env=env)

    @classmethod
    def from_file(
            cls,
            file: Union[str, Path, TextIO],
            format: Optional[str] = None,
            env: Optional[Environment] = None,
    ) -> "Markup":
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

            if env is None:
                filename = Path(file)
            else:
                filename = env.find_file(file)
                if not filename:
                    raise IOError(f"Can not find '{file}'")

            text = filename.read_text()

        fm, markup = split_front_matter_and_markup(text)

        return cls(
            markup=markup,
            format=format,
            front_matter=fm,
            filename=filename,
        )

    def get_front_matter_value(self, key: str, default=None, type_check: Optional[Type] = None):
        """
        Return a value from the markups front-matter, if present.

        Note that **any** present front-matter value will override the default, even None

        :param key: str, The key
        :param default: any default value if the key is not present in front-matter
        :param type_check: optional type that the front-matter value should have
            Otherwise an exception is thrown

        :return: front-matter value or default value
        """
        if self.front_matter and key in self.front_matter:
            value = self.front_matter[key]
            if type_check is not None:
                if not isinstance(value, type_check):
                    raise TypeError(
                        f"Expected type '{type_check.__name__}' for front-matter value '{key}'"
                        f", got '{type(value).__name__}'"
                    )
            return value
        return default

    def markup(self, context: Optional[dict] = None, env: Optional[Environment] = None) -> str:
        if self._markup is None:
            if "{%" not in self.markup_template and "{{" not in self.markup_template:
                self._markup = self.markup_template
            else:
                self._render_template(context=context, env=env)
            if not self._markup.endswith("\n"):
                self._markup += "\n"
        return self._markup

    def to_html(self, context: Optional[dict] = None, env: Optional[Environment] = None) -> str:
        if self.format == "html":
            return self.markup(context=context, env=env)

        elif self.format == "md":
            from marko import Markdown
            from marko.html_renderer import HTMLRenderer
            md = Markdown()
            doc = md.parse(self.markup(context=context, env=env))
            return HTMLRenderer().render(doc)

        else:
            raise NotImplementedError(self.format)

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
