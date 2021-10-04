import unittest

from xappt.plugins.interfaces.test import TestInterface


class TestDataTypesTool(unittest.TestCase):
    def test_import(self):
        from xappt.plugins.tools.examples.data_types import DataTypes
        interface = TestInterface()
        interface.add_tool(DataTypes)
        self.assertEqual(0, interface.run())
