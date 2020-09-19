import re
import unittest

from xappt.__version__ import __version__

VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


class TestVersion(unittest.TestCase):
    def test_version(self):
        self.assertIsNotNone(VERSION_RE.match(__version__))
