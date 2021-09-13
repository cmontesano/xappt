import os
import unittest

from typing import Optional
from unittest import mock

from xappt.models.plugins.interface import BaseInterface
from xappt.models.plugins.tool import BaseTool
from xappt.utilities.path.temp_path import temporary_path

from tests.managers.test_plugin_manager import temp_register


class InterfacePlugin(BaseInterface):
    def __init__(self):
        super().__init__()

    def record_method(self, method_name: str, *args, **kwargs):
        if method_name not in self.tool_data:
            self.tool_data[method_name] = {'called': []}
        self.tool_data[method_name]['called'].append((args, kwargs))

    def message(self, message: str):
        self.record_method('message', message)

    def warning(self, message: str):
        self.record_method('warning', message)

    def error(self, message: str, *, details: Optional[str] = None):
        self.record_method('error', message, details)

    def ask(self, message: str) -> bool:
        self.record_method('ask', message)
        return True

    def progress_start(self):
        self.record_method('progress_start')

    def progress_update(self, message: str, percent_complete: float):
        self.record_method('progress_update', message, percent_complete)

    def progress_end(self):
        self.record_method('progress_end')

    def invoke(self, plugin: BaseTool, **kwargs) -> int:
        self.record_method('invoke', plugin, **kwargs)
        return self.get_tool(self.current_tool_index)(interface=self).execute()

    def run(self) -> int:
        return super().run()


class ToolPluginA(BaseTool):
    def execute(self, **kwargs) -> int:
        return 0


class ToolPluginB(BaseTool):
    def execute(self, **kwargs) -> int:
        return 1


class TestBaseInterface(unittest.TestCase):
    def test_run(self):
        iface = InterfacePlugin()
        iface.run()
        self.assertNotIn("invoke", iface.tool_data)
        self.assertEqual(-1, iface.current_tool_index)

    def test_run_with_tool(self):
        iface = InterfacePlugin()
        iface.add_tool(ToolPluginA)
        iface.run()
        self.assertEqual(1, len(iface.tool_data['invoke']['called']))
        args, kwargs = iface.tool_data['invoke']['called'][0]
        self.assertIsInstance(args[0], BaseTool)

    def test_run_with_tools(self):
        iface = InterfacePlugin()
        iface.add_tool(ToolPluginA)
        iface.add_tool(ToolPluginA)
        iface.add_tool(ToolPluginA)
        iface.run()
        self.assertEqual(2, iface.current_tool_index)

    def test_run_failure(self):
        iface = InterfacePlugin()
        iface.add_tool(ToolPluginA)
        iface.add_tool(ToolPluginB)
        result = iface.run()
        self.assertEqual(1, result)

    def test_run_with_tool_string(self):
        with temp_register(ToolPluginA):
            iface = InterfacePlugin()
            iface.add_tool("toolplugina")
            iface.run()
            self.assertEqual(1, len(iface.tool_data['invoke']['called']))
            args, kwargs = iface.tool_data['invoke']['called'][0]
            self.assertIsInstance(args[0], BaseTool)

    def test_tool_chain(self):
        iface = InterfacePlugin()
        iface.add_tool(ToolPluginA)
        self.assertEqual(1, iface.tool_count)
        iface.add_tool(ToolPluginA)
        self.assertEqual(2, iface.tool_count)
        self.assertIs(ToolPluginA, iface.get_tool(0))
        iface.clear_tool_chain()
        self.assertEqual(0, iface.tool_count)

    def test_stdio_callbacks(self):
        m = mock.Mock()
        stdout_write = m.stdout_write()
        stderr_write = m.stderr_write()
        iface = InterfacePlugin()
        iface.on_write_stdout.add(stdout_write)
        iface.on_write_stderr.add(stderr_write)
        iface.write_stdout("writing stdout")
        iface.write_stderr("writing stderr")
        self.assertTrue(stdout_write.called_with("writing stdout"))
        self.assertTrue(stderr_write.called_with("writing stderr"))

    def test_run_subprocess(self):
        test_directory_name = "test-dir"
        if os.name == "posix":
            mkdir_cmd = ("mkdir", test_directory_name)
        elif os.name == "nt":
            mkdir_cmd = ("cmd", "/c", "mkdir", test_directory_name)
        else:
            raise NotImplementedError
        iface = InterfacePlugin()
        with temporary_path() as tmp:
            result = iface.run_subprocess(mkdir_cmd, cwd=tmp, shell=False)
            self.assertEqual(0, result)
            self.assertTrue(tmp.joinpath(test_directory_name).is_dir())
