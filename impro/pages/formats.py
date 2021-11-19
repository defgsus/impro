from pathlib import Path
from typing import Union, Optional


INPUT_FORMATS = (
    "md",
)


def get_filename_format(filename: Union[str, Path]) -> Optional[str]:
    fn = str(filename).lower()
    if fn.endswith(".md"):
        return "md"
