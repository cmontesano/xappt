import os
import pathlib
import shutil
import tempfile
import unittest

from xappt.utilities import search_files
from xappt.utilities import unique_path, UniqueMode
from xappt.utilities import temporary_path

FILES = (
    "file01.txt",
    "file02.py",
    "file03.sh",
    "1/file01.txt",
    "1/file02.py",
    "1/file03.sh",
    "1/1/file01.txt",
    "1/1/file02.py",
    "1/1/file03.sh",
    "1/1/1/file01.txt",
    "1/1/1/file02.py",
    "1/1/1/file03.sh",
    "2/file01.txt",
    "2/file02.py",
    "2/file03.sh",
    "2/2/file01.txt",
    "2/2/file02.py",
    "2/2/file03.sh",
    "2/2/2/file01.txt",
    "2/2/2/file02.py",
    "2/2/2/file03.sh",
)


class TestFindFiles(unittest.TestCase):
    tmp = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = pathlib.Path(tempfile.mkdtemp())

        for f in FILES:
            path = cls.tmp.joinpath(*f.split("/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp)

    def test_find_files(self):
        files = list(search_files(self.tmp, patterns="*.txt"))
        self.assertEqual(len(files), 1)

    def test_find_files_recursive(self):
        files = list(search_files(self.tmp, patterns="*.txt", recursive=True))
        self.assertEqual(len(files), 7)

    def test_find_files_recursive_multiple_patterns(self):
        files = list(search_files(self.tmp, patterns=("*.txt", "*.py"), recursive=True))
        self.assertEqual(len(files), 14)


# noinspection DuplicatedCode
class TestGetUniqueName(unittest.TestCase):
    def test_get_unique_name_random(self):
        with temporary_path() as tmp:
            for _ in range(10):
                file_path = unique_path(tmp.joinpath("file.txt"), mode=UniqueMode.RANDOM)
                file_path.touch()
            self.assertEqual(len(os.listdir(tmp)), 10)

    def test_get_unique_name_integer(self):
        with temporary_path() as tmp:
            for _ in range(10):
                file_path = unique_path(tmp.joinpath("file.txt"), mode=UniqueMode.INTEGER)
                file_path.touch()
            self.assertEqual(len(os.listdir(tmp)), 10)

    def test_get_unique_name_bad_mode(self):
        with temporary_path() as tmp:
            with self.assertRaises(NotImplementedError):
                # noinspection PyTypeChecker
                _ = unique_path(tmp.joinpath("file.txt"), mode=9999)

    def test_get_unique_name_force(self):
        with temporary_path() as tmp:
            base_file = tmp.joinpath("file.txt")
            self.assertFalse(base_file.is_file())
            file_path = unique_path(base_file, mode=UniqueMode.INTEGER, length=4, delimiter="_", force=True)
            self.assertEqual(file_path.name, "file_0001.txt")
