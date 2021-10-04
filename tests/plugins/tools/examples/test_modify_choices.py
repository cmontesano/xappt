import unittest

from xappt.plugins.interfaces.test import TestInterface


class TestModifyChoicesTool(unittest.TestCase):
    def test_import(self):
        from xappt.plugins.tools.examples.modify_choices import ModifyChoices
        interface = TestInterface()
        interface.add_tool(ModifyChoices)
        self.assertEqual(0, interface.run())
