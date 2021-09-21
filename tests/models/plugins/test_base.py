import unittest

from xappt.models.mixins.config import ConfigMixin
from xappt.models.plugins.base import BasePlugin
from xappt.utilities.path.temp_path import temporary_path


class TestBasePlugin(unittest.TestCase):
    def test_subclass(self):
        class TestPlugin(BasePlugin):
            pass

        self.assertTrue(issubclass(TestPlugin, ConfigMixin))

    def test_data(self):
        with temporary_path() as tmp:
            class TestPlugin(BasePlugin):
                def __init__(self):
                    super().__init__()
                    self.config_path = tmp.joinpath("config.cfg")
                    self.data = {}

                def init_config(self):
                    self.add_config_item(key="test",
                                         saver=lambda: self.data,
                                         loader=lambda x: self.data.update(x),
                                         default={})

            tp = TestPlugin()
            self.assertDictEqual({}, tp.data)
            tp.data['test'] = 'value'
            tp.save_config()
            tp.data.clear()
            tp.load_config()
            self.assertDictEqual({'test': 'value'}, tp.data)

    def test_default_name(self):
        class TestPlugin(BasePlugin):
            pass

        self.assertEqual("testplugin", TestPlugin.name())

    def test_default_collection(self):
        class TestPlugin(BasePlugin):
            pass

        self.assertEqual("", TestPlugin.collection())

    def test_default_help(self):
        class TestPlugin(BasePlugin):
            pass

        self.assertEqual("", TestPlugin.help())

    def test_init_config(self):
        class TestPlugin(BasePlugin):
            pass

        tp = TestPlugin()

        self.assertEqual(0, len(tp._registry))

    def test_no_init_config(self):
        class TestPlugin(BasePlugin):
            def init_config(self):
                pass

        tp = TestPlugin()

        self.assertEqual(0, len(tp._registry))
