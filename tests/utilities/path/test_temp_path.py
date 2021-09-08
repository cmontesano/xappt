import os
import shutil
import stat
import unittest

from xappt.utilities import temporary_path
from xappt.utilities.path.temp_path import handle_remove_readonly


class TestTempPath(unittest.TestCase):
    def test_temp_path(self):
        with temporary_path() as tmp:
            self.assertTrue(tmp.is_dir())
        self.assertFalse(tmp.is_dir())

    def test_temp_path_readonly(self):
        with temporary_path() as tmp:
            ro_path = tmp.joinpath("ro-folder")
            ro_path.mkdir()
            ro_file = ro_path.joinpath("ro-file")
            with ro_file.open("w") as fp:
                fp.write("test")
            ro_file.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            ro_path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            with self.assertRaises(PermissionError):
                with ro_file.open("w") as fp:
                    fp.write("test")
            self.assertTrue(tmp.is_dir())
        self.assertFalse(tmp.is_dir())

    def test_handle_remove_readonly(self):
        with temporary_path() as tmp:
            fake_path = tmp.joinpath("fake")
            with self.assertRaises(FileNotFoundError):
                shutil.rmtree(fake_path, onerror=handle_remove_readonly)
