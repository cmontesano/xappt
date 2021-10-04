import unittest

from xappt.plugins.interfaces.test import TestInterface


class TestToolChainingTool(unittest.TestCase):
    def test_import(self):
        from xappt.plugins.tools.examples.tool_chaining import ToolChaining
        interface = TestInterface()
        interface.add_tool(ToolChaining)
        interface.tool_data['next_tool'] = 'none (quit)'
        self.assertEqual(0, interface.run())
