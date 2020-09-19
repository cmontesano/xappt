import os
import pathlib
import shutil
import tempfile
import unittest

from xappt.utilities import find_files
from xappt.utilities import get_unique_name, UniqueMode
from xappt.utilities import temp_path

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
        cls.tmp = tempfile.mkdtemp()

        for f in FILES:
            path = os.path.join(cls.tmp, *f.split("/"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            pathlib.Path(path).touch()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp)

    def test_find_files(self):
        files = list(find_files(self.tmp, "*.txt"))
        self.assertEqual(len(files), 1)

    def test_find_files_recursive(self):
        files = list(find_files(self.tmp, "*.txt", recursive=True))
        self.assertEqual(len(files), 7)

    def test_find_files_recursive_multiple_patterns(self):
        files = list(find_files(self.tmp, ("*.txt", "*.py"), recursive=True))
        self.assertEqual(len(files), 14)


# noinspection DuplicatedCode
class TestGetUniqueName(unittest.TestCase):
    def test_get_unique_name_random(self):
        with temp_path() as tmp:
            for _ in range(10):
                file_path = get_unique_name(os.path.join(tmp, "file.txt"),
                                            mode=UniqueMode.RANDOM)
                pathlib.Path(file_path).touch()
            self.assertEqual(len(os.listdir(tmp)), 10)

    def test_get_unique_name_integer(self):
        with temp_path() as tmp:
            for _ in range(10):
                file_path = get_unique_name(os.path.join(tmp, "file.txt"),
                                            mode=UniqueMode.INTEGER)
                pathlib.Path(file_path).touch()
            self.assertEqual(len(os.listdir(tmp)), 10)

    def test_get_unique_name_bad_mode(self):
        with temp_path() as tmp:
            with self.assertRaises(NotImplementedError):
                # noinspection PyTypeChecker
                _ = get_unique_name(os.path.join(tmp, "file.txt"), mode=9999)

    def test_get_unique_name_force(self):
        with temp_path() as tmp:
            base_file = os.path.join(tmp, "file.txt")
            self.assertFalse(os.path.isfile(base_file))
            file_path = get_unique_name(base_file, mode=UniqueMode.INTEGER,
                                        length=4, delimiter="_", force=True)
            self.assertEqual(os.path.basename(file_path), "file_0001.txt")
