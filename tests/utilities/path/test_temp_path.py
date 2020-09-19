import os
import shutil
import stat
import unittest

from xappt.utilities import temp_path
from xappt.utilities.path.temp_path import handle_remove_readonly


class TestTempPath(unittest.TestCase):
    def test_temp_path(self):
        with temp_path() as tmp:
            self.assertTrue(os.path.isdir(tmp))
        self.assertFalse(os.path.isdir(tmp))

    def test_temp_path_readonly(self):
        with temp_path() as tmp:
            ro_path = os.path.join(tmp, "ro-folder")
            os.makedirs(ro_path)
            ro_file = os.path.join(ro_path, "ro-file")
            with open(ro_file, "w") as fp:
                fp.write("test")
            os.chmod(ro_file, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            os.chmod(ro_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            with self.assertRaises(PermissionError):
                with open(ro_file, "w") as fp:
                    fp.write("test")
            self.assertTrue(os.path.isdir(tmp))
        self.assertFalse(os.path.isdir(tmp))

    def test_handle_remove_readonly(self):
        with temp_path() as tmp:
            fake_path = os.path.join(tmp, "fake")
            with self.assertRaises(FileNotFoundError):
                shutil.rmtree(fake_path, onerror=handle_remove_readonly)
