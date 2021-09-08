import contextlib
import logging
import os
import shutil
import unittest

from typing import Generator, Optional, Type
from unittest.mock import patch

from xappt.managers import plugin_manager
from xappt.models.plugins.base import BasePlugin
from xappt.models import BaseTool, BaseInterface
from xappt.utilities.path import temporary_path
from xappt.constants import *

DATA_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "data"))
TEST_PLUGINS_ARCHIVE = os.path.join(DATA_PATH, "xappt_test_plugins.tar.gz")


@contextlib.contextmanager
def temp_register(class_name: Type[BasePlugin], **kwargs) -> Generator[str, None, None]:
    if issubclass(class_name, BaseTool):
        plugin_type = PLUGIN_TYPE_TOOL
    elif issubclass(class_name, BaseInterface):
        plugin_type = PLUGIN_TYPE_INTERFACE
    else:
        raise NotImplementedError
    name = class_name.name()
    active = kwargs.get('active', True)
    visible = kwargs.get('visible', True)
    try:
        plugin_manager.register_plugin(class_name, active=active, visible=visible)
        yield name
    finally:
        try:
            del plugin_manager.PLUGIN_REGISTRY[plugin_type][name]
        except KeyError:
            pass


class RealToolPlugin(BaseTool):
    def execute(self, **kwargs) -> int:
        pass


class RealInterfacePlugin(BaseInterface):
    def __init__(self):
        super().__init__()

    def invoke(self, plugin: BaseTool, **kwargs):
        pass

    def message(self, message: str):
        pass

    def warning(self, message: str):
        pass

    def error(self, message: str, *, details: Optional[str] = None):
        pass

    def ask(self, message: str) -> bool:
        pass

    def progress_start(self):
        pass

    def progress_update(self, message: str, percent_complete: float):
        pass

    def progress_end(self):
        pass

    def run(self) -> int:
        pass


class TestPluginManager(unittest.TestCase):
    TEST_PLUGINS = {
        PLUGIN_TYPE_TOOL: {
            'plugins': [
                RealToolPlugin,
            ],
            'get_plugin': plugin_manager.get_tool_plugin,
            'get_registered': plugin_manager.registered_tools,
        },
        PLUGIN_TYPE_INTERFACE: {
            'plugins': [
                RealInterfacePlugin,
            ],
            'get_plugin': plugin_manager.get_interface_plugin,
            'get_registered': plugin_manager.registered_interfaces,
        },
    }

    def setUp(self) -> None:
        logging.disable(logging.CRITICAL)

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)

    def test_register_non_plugin(self):
        class FakePlugin:
            pass

        with self.assertRaises(NotImplementedError):
            plugin_manager.register_plugin(FakePlugin)

    def test_register_inactive_plugin(self):
        plugin_manager.register_plugin(RealToolPlugin, active=False)
        with self.assertRaises(ValueError):
            plugin_manager.get_tool_plugin(RealToolPlugin.name())

    def test_register_plugins(self):
        for _, plugin_data in self.TEST_PLUGINS.items():
            for plugin_class in plugin_data['plugins']:
                with temp_register(plugin_class) as name:
                    self.assertIsNotNone(plugin_data['get_plugin'](name))
                with self.assertRaises(ValueError):
                    plugin_data['get_plugin'](name)

    def test_reregister(self):
        with temp_register(RealToolPlugin):
            plugin_count = len(plugin_manager.PLUGIN_REGISTRY[PLUGIN_TYPE_TOOL])
            result = plugin_manager._add_plugin_to_registry(RealToolPlugin, visible=False)
            self.assertFalse(result)
            self.assertEqual(len(plugin_manager.PLUGIN_REGISTRY[PLUGIN_TYPE_TOOL]), plugin_count)

    def test_list_registered_plugins(self):
        for plugin_type, plugin_data in self.TEST_PLUGINS.items():
            for plugin_class in plugin_data['plugins']:
                with temp_register(plugin_class) as name:
                    self.assertIsNotNone(plugin_data['get_plugin'](name))
                    all_plugins = list(plugin_data['get_registered']())
                    self.assertIn((name, plugin_class), all_plugins)

    def test_list_registered_plugins_hidden(self):
        for plugin_type, plugin_data in self.TEST_PLUGINS.items():
            for plugin_class in plugin_data['plugins']:
                with temp_register(plugin_class, visible=False) as name:
                    all_plugins = list(plugin_data['get_registered']())
                    self.assertNotIn((name, plugin_class), all_plugins)

    def test_register_bad_collection_int(self):
        class BadCollectionPluginInt(RealToolPlugin):
            @classmethod
            def collection(cls):
                return 1

        with self.assertRaises(AttributeError):
            with temp_register(BadCollectionPluginInt):
                pass

    def test_register_bad_collection_str(self):
        class BadCollectionPluginStr(RealToolPlugin):
            @classmethod
            def collection(cls):
                return ""

        plugin_count = len(plugin_manager.PLUGIN_REGISTRY[PLUGIN_TYPE_TOOL])
        result = plugin_manager._add_plugin_to_registry(BadCollectionPluginStr, visible=False)
        self.assertFalse(result)
        self.assertEqual(len(plugin_manager.PLUGIN_REGISTRY[PLUGIN_TYPE_TOOL]), plugin_count)

    def test_get_interface_default(self):
        # let's ensure that the default interface is registered
        self.assertIn(INTERFACE_DEFAULT, plugin_manager.PLUGIN_REGISTRY[PLUGIN_TYPE_INTERFACE].keys())
        # and that there is no outside interference
        self.assertEqual(os.environ.get(INTERFACE_ENV, INTERFACE_DEFAULT), INTERFACE_DEFAULT)
        interface_instance = plugin_manager.get_interface()
        self.assertEqual(interface_instance.name(), INTERFACE_DEFAULT)
        self.assertIsInstance(interface_instance, BaseInterface)

    def test_get_interface_custom(self):
        with temp_register(RealInterfacePlugin) as name:
            interface_instance = plugin_manager.get_interface(name)
            self.assertEqual(interface_instance.name(), name)
            self.assertIsInstance(interface_instance, RealInterfacePlugin)

    def test_discover_plugins(self):
        self.assertTrue(os.path.isfile(TEST_PLUGINS_ARCHIVE))
        with temporary_path() as tmp:
            shutil.unpack_archive(TEST_PLUGINS_ARCHIVE, tmp)
            with patch.dict('os.environ', {PLUGIN_PATH_ENV: str(tmp)}):
                plugin_manager.discover_plugins()
                plugin_manager.discover_plugins()  # intentionally called twice!
                all_tool_plugins = [p[0] for p in plugin_manager.registered_tools()]
                self.assertIn("toolplugin01", all_tool_plugins)
                self.assertIn("toolplugin02", all_tool_plugins)
                # ToolPlugin03 has a bad import... it should not load
                self.assertNotIn("toolplugin03", all_tool_plugins)
