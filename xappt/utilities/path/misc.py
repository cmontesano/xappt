import enum
import fnmatch
import os
import random
import re
import string

from typing import Generator, Sequence, Union

RAND_CHARS = string.ascii_letters + string.digits


class UniqueMode(enum.Enum):
    RANDOM = 0
    INTEGER = 1


def find_files(path: str, patterns: Union[str, Sequence], *, recursive: bool = False) -> Generator[str, None, None]:
    """ Search `path` for files, optionally *recursively*, and yield files that match `pattern`.
    Note that `pattern` expects an `fnmatch` compatible pattern (e.g. `*.py`), or a list/tuple of patterns.
    """
    if isinstance(patterns, str):
        patterns = [patterns]
    pattern_regex = re.compile('|'.join([fnmatch.translate(p) for p in patterns]))

    if recursive:
        for root, dirs, files in os.walk(path):
            for f in files:
                if pattern_regex.match(f):
                    yield os.path.join(root, f)
    else:
        for item in os.scandir(path):
            if pattern_regex.match(item.name):
                yield item.path


def get_unique_name(path: str, *, mode: UniqueMode = UniqueMode.RANDOM, **kwargs) -> str:
    """ Generate a unique file name by adding either random characters or sequential integers.

    >>> file_path = "/path/to/file.txt"
    >>> my_delimiter = "-"
    >>> unique_path = get_unique_name(file_path, mode=UniqueMode.RANDOM, length=8, force=True, delimiter=my_delimiter)
    >>> len(unique_path) == len(file_path) + 8 + len(my_delimiter)
    True
    >>> unique_path = get_unique_name(file_path, mode=UniqueMode.INTEGER, length=3, force=True, delimiter=my_delimiter)
    >>> len(unique_path) == len(file_path) + 3 + len(my_delimiter)
    True
    >>> unique_path.endswith(f"file{my_delimiter}001.txt")
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
