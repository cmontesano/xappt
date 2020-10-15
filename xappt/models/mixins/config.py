import os
import json

from collections import namedtuple
from typing import Any, Callable, List, Optional

ConfigItem = namedtuple("ConfigItem", ("key", "saver", "loader", "default"))


class ConfigMixin:
    def __init__(self):
        super().__init__()
        self.settings_file_path: Optional[str] = None
        self._registry: List[ConfigItem] = []

    def add_config_item(self, key: str, *, saver: Callable, loader: Callable, default: Any = None):
        self._registry.append(ConfigItem(key, saver, loader, default))

    def _check_settings_file_name(self):
        if self.settings_file_path is None:
            raise RuntimeError("`setting_file_name` has not been set")

    def load_config(self):
        self._check_settings_file_name()

        loaded_settings_raw = {}
        try:
            with open(self.settings_file_path, "r") as fp:
                try:
                    loaded_settings_raw = json.load(fp)
                except json.JSONDecodeError:
                    pass
        except FileNotFoundError:
            pass

        for item in self._registry:
            value = loaded_settings_raw.get(item.key, item.default)
            # noinspection PyBroadException
            try:
                item.loader(value)
            except BaseException:
                pass

    def save_config(self):
        self._check_settings_file_name()

        settings_dict = {}
        for item in self._registry:
            value = item.saver()
            settings_dict[item.key] = value

        os.makedirs(os.path.dirname(self.settings_file_path), exist_ok=True)
        with open(self.settings_file_path, "w") as fp:
            json.dump(settings_dict, fp, indent=2)
