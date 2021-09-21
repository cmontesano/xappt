import enum
import fnmatch
import os
import pathlib
import platform
import random
import re
import string
import warnings

from typing import Generator, Sequence, Union

RAND_CHARS = string.ascii_letters + string.digits


class UniqueMode(enum.Enum):
    RANDOM = 0
    INTEGER = 1


def find_files(path: str, patterns: Union[str, Sequence], *, recursive: bool = False) -> Generator[str, None, None]:
    """ Search `path` for files, optionally *recursively*, and yield files that match `pattern`.
    Note that `pattern` expects an `fnmatch` compatible pattern (e.g. `*.py`), or a list/tuple of patterns.
    """
    warnings.warn("Call to deprecated function `find_files`. Use `search_files` instead.", DeprecationWarning)
    if isinstance(patterns, str):
        patterns = [patterns]
    pattern_regex = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if recursive:
        for root, dirs, files in os.walk(path):
            for f in files:
                if pattern_regex.match(f):
                    yield os.path.join(root, f)
    else:
        for item in os.scandir(path):  # type: os.DirEntry
            if pattern_regex.match(item.name):
                yield item.path


def search_files(search_path: pathlib.Path, **kwargs) -> Generator[pathlib.Path, None, None]:
    """ Search `search_path` for files, optionally *recursively*, and yield paths that match `pattern`.
    Note that `pattern` expects an `fnmatch` compatible pattern (e.g. `*.py`), or a list/tuple of patterns.
    """
    patterns: Union[str, Sequence] = kwargs['patterns']
    recursive: bool = kwargs.get('recursive', False)

    if isinstance(patterns, str):
        patterns = [patterns]
    pattern_regex = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if recursive:
        for root, dirs, files in os.walk(search_path):
            root_path = pathlib.Path(root)
            for f in files:
                if pattern_regex.match(f):
                    yield root_path.joinpath(f)
    else:
        for item in search_path.iterdir():
            if not item.is_file():
                continue
            if pattern_regex.match(item.name):
                yield item


def get_unique_name(path: str, *, mode: UniqueMode = UniqueMode.RANDOM, **kwargs) -> str:
    """ Generate a unique file name by adding either random characters or sequential integers.

    >>> file_path = "/path/to/file.txt"
    >>> my_delimiter = "-"
    >>> unique_file = get_unique_name(file_path, mode=UniqueMode.RANDOM, length=8, force=True, delimiter=my_delimiter)
    >>> len(unique_file) == len(file_path) + 8 + len(my_delimiter)
    True
    >>> unique_file = get_unique_name(file_path, mode=UniqueMode.INTEGER, length=3, force=True, delimiter=my_delimiter)
    >>> len(unique_file) == len(file_path) + 3 + len(my_delimiter)
    True
    >>> unique_file.endswith(f"file{my_delimiter}001.txt")
    True

    """
    warnings.warn("Call to deprecated function `get_unique_name`. Use `unique_path` instead.", DeprecationWarning)

    delimiter = kwargs.get('delimiter', "-")
    max_iterations = kwargs.get("max_iterations", 9999)
    force_unique = kwargs.get("force", False)

    if mode == UniqueMode.RANDOM:
        length = kwargs.get("length", 8)

        def unique_key_fn(_: int) -> str:
            return "".join(random.choices(RAND_CHARS, k=length))

    elif mode == UniqueMode.INTEGER:
        length = kwargs.get("length", 3)

        def unique_key_fn(iteration: int) -> str:
            return str(iteration).rjust(length, "0")

    else:
        raise NotImplementedError

    if not force_unique and not os.path.isfile(path):
        return path

    directory, file_name = os.path.split(path)
    file_name, extension = os.path.splitext(file_name)

    for i in range(max_iterations):
        unique_key = unique_key_fn(i + 1)
        new_file_name = f"{file_name}{delimiter}{unique_key}{extension}"
        check_path = os.path.join(directory, new_file_name)
        if not os.path.isfile(check_path):
            return check_path


def unique_path(path: pathlib.Path, *, mode: UniqueMode = UniqueMode.RANDOM, **kwargs) -> pathlib.Path:
    """ Generate a unique file name by adding either random characters or sequential integers.

    >>> file_path = pathlib.Path("/path/to/file.txt")
    >>> my_delimiter = "-"
    >>> unique = unique_path(file_path, mode=UniqueMode.RANDOM, length=8, force=True, delimiter=my_delimiter)
    >>> len(unique.name) == len(file_path.name) + 8 + len(my_delimiter)
    True
    >>> unique = unique_path(file_path, mode=UniqueMode.INTEGER, length=3, force=True, delimiter=my_delimiter)
    >>> len(unique.name) == len(file_path.name) + 3 + len(my_delimiter)
    True
    >>> unique.name == f"file{my_delimiter}001.txt"
    True
    """

    delimiter = kwargs.get('delimiter', "-")
    max_iterations = kwargs.get("max_iterations", 9999)
    force_unique = kwargs.get("force", False)

    if mode == UniqueMode.RANDOM:
        length = kwargs.get("length", 8)

        def unique_key_fn(_: int) -> str:
            return "".join(random.choices(RAND_CHARS, k=length))

    elif mode == UniqueMode.INTEGER:
        length = kwargs.get("length", 3)

        def unique_key_fn(iteration: int) -> str:
            return str(iteration).rjust(length, "0")

    else:
        raise NotImplementedError

    if not force_unique and not path.is_file():
        return path

    for i in range(max_iterations):
        unique_key = unique_key_fn(i + 1)
        check_path = path.with_name(f"{path.stem}{delimiter}{unique_key}{path.suffix}")
        if not check_path.is_file():
            return check_path

    raise FileNotFoundError(f"Could not generate a unique name after {max_iterations} iterations")


def user_data_path() -> pathlib.Path:
    if platform.system() == 'Windows':
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        key_value, key_type = winreg.QueryValueEx(key, 'AppData')
        data_path = pathlib.Path(key_value).resolve(strict=False)
    elif platform.system() == 'Darwin':
        data_path = pathlib.Path('~/Library/Application Support/').expanduser()
    elif platform.system() == 'Linux':
        data_path = pathlib.Path(os.getenv('XDG_DATA_HOME', "~/.local/share")).expanduser()
    else:
        raise NotImplementedError
    return data_path


if __name__ == '__main__':
    import doctest
    doctest.testmod()
