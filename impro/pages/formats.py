import os
from typing import Union, Optional


INPUT_FORMATS = (
    "md",
)


def get_filename_format(filename: Union[str, os.PathLike]) -> Optional[str]:
    fn = str(filename).lower()
    if fn.endswith(".md"):
        return "md"
