import json
import tempfile
import unittest

from unittest import mock

from xappt.models.mixins.config import ConfigMixin
from xappt.utilities.path.temp_path import temporary_path


class TestConfigMixin(unittest.TestCase):
    def test_save_config_no_file(self):
        cm = ConfigMixin()
        with self.assertRaises(RuntimeError) as err:
            cm.save_config()
        self.assertIn("has not been set", str(err.exception))

    def test_save_config_bad_path_int(self):
        cm = ConfigMixin()
        cm.config_path = 82735
        with self.assertRaises(RuntimeError) as err:
            cm.save_config()
        self.assertIn("is not an instance of", str(err.exception))

    def test_save_config_bad_path_str(self):
        with tempfile.NamedTemporaryFile() as config_file:
            cm = ConfigMixin()
            cm.config_path = config_file.name
            with self.assertRaises(RuntimeError) as err:
                cm.save_config()
            self.assertIn("is not an instance of", str(err.exception))

    def test_save_config_bad_path_exists(self):
        cm = ConfigMixin()
        with temporary_path() as tmp:
            config_folder = tmp.joinpath("config")
            config_folder.mkdir(parents=True)
            cm.config_path = config_folder
            with self.assertRaises(FileExistsError) as err:
                cm.save_config()
            self.assertIn("is an existing directory name", str(err.exception))

    def test_save_config(self):
        cm = ConfigMixin()
        cm.add_config_item(key="test-bool", saver=lambda: True, loader=lambda x: x, default=True)
        cm.add_config_item(key="test-int", saver=lambda: 123, loader=lambda x: x, default=456)
        with temporary_path() as tmp:
            cm.config_path = tmp.joinpath("config")
            cm.save_config()
            with cm.config_path.open("r") as fp:
                saved_data = json.load(fp)
        self.assertIn("test-bool", saved_data.keys())
        self.assertIn("test-int", saved_data.keys())
        self.assertTrue(saved_data["test-bool"])
        self.assertEqual(123, saved_data["test-int"])

    def test_load_config_default_no_file(self):
        m = mock.Mock()
        loader = m.a()
        cm = ConfigMixin()
        cm.add_config_item(key="test-int", saver=lambda: 123, loader=loader, default=456)
        with temporary_path() as tmp:
            cm.config_path = tmp.joinpath("config")
            cm.load_config()
            self.assertTrue(loader.called)
            # not yet saved, should be called with default value
            self.assertTrue(loader.called_with('456'))

    def test_load_config_default_no_data(self):
        m = mock.Mock()
        loader = m.a()
        cm = ConfigMixin()
        cm.add_config_item(key="test-int", saver=lambda: 123, loader=loader, default=456)
        with temporary_path() as tmp:
            cm.config_path = tmp.joinpath("config")
            cm.config_path.touch()
            cm.load_config()
            self.assertTrue(loader.called)
            # not yet saved, should be called with default value
            self.assertTrue(loader.called_with('456'))

    def test_load_config_saved(self):
        m = mock.Mock()
        loader = m.a()
        cm = ConfigMixin()
        cm.add_config_item(key="test-int", saver=lambda: 123, loader=loader, default=456)
        with temporary_path() as tmp:
            cm.config_path = tmp.joinpath("config")
            cm.save_config()
            cm.load_config()
            self.assertTrue(loader.called)
            self.assertTrue(loader.called_with('123'))

    def test_load_config_errors(self):
        def loader_with_errors(value: int):
            raise RuntimeError

        cm = ConfigMixin()
        cm.add_config_item(key="test-int", saver=lambda: 123, loader=loader_with_errors, default=456)
        with temporary_path() as tmp:
            cm.config_path = tmp.joinpath("config")
            cm.save_config()
            try:
                cm.load_config()
            except RuntimeError:
                self.fail("No errors should be raised.")
