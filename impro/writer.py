import os
from pathlib import Path
from typing import List, Tuple, Dict, Union, Optional


class Writer:

    def __init__(self, root: Union[str, os.PathLike]):
        self.root = Path(root)
        if not self.root.is_absolute():
            raise ValueError(
                f"Absolute dir required for {self.__class__.__name__} root, got '{self.root}'"
            )

    def write(self, filename: Union[str, os.PathLike], content: Union[str, bytes]):
        self._check_filename_and_content(filename, content)
        raise NotImplementedError

    def _check_filename_and_content(self, filename: Union[str, os.PathLike], content: Union[str, bytes]):
        filename = Path(filename)
        if filename.is_absolute():
            raise ValueError(
                f"Absolute filenames are not supported by {self.__class__.__name__}: '{filename}'"
            )

        if not isinstance(content, (str, bytes)):
            raise TypeError(
                f"{self.__class__.__name__} expected str or bytes, got '{type(content).__name__}' for '{filename}'"
            )


class FileWriter(Writer):

    def __init__(self, root: Union[str, os.PathLike]):
        super().__init__(root)
        self.files: List[Path] = []

    def write(self, filename: Union[str, os.PathLike], content: Union[str, bytes]):
        self._check_filename_and_content(filename, content)

        full_name = self.root / filename
        full_path = full_name.parent
        os.makedirs(full_path, exist_ok=True)

        if isinstance(content, str):
            full_name.write_text(content)
        else:
            full_name.write_bytes(content)

        self.files.append(full_name)


class MemoryWriter(FileWriter):

    def __init__(self, root: Union[str, os.PathLike] = "/"):
        super().__init__(root=root)
        self.files: Dict[Path, Union[str, bytes]] = dict()

    def write(self, filename: Union[str, os.PathLike], content: Union[str, bytes]):
        self._check_filename_and_content(filename, content)

        full_name = self.root / filename
        self.files[full_name] = content
