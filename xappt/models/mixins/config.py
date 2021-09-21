import pathlib
import json

from collections import namedtuple
from typing import Any, Callable, List, Optional

ConfigItem = namedtuple("ConfigItem", ("key", "saver", "loader", "default"))


class ConfigMixin:
    def __init__(self):
        super().__init__()
        self._config_path: Optional[pathlib.Path] = None
        self._registry: List[ConfigItem] = []

    def add_config_item(self, key: str, *, saver: Callable, loader: Callable, default: Any = None):
        self._registry.append(ConfigItem(key, saver, loader, default))

    def _check_settings_file_name(self):
        if self.config_path is None:
            raise RuntimeError("`config_path` has not been set")
        if not isinstance(self.config_path, pathlib.Path):
            raise RuntimeError(f"{self.config_path!r} is not an instance of `pathlib.Path`")
        if self.config_path.is_dir():
            raise FileExistsError(f"{self.config_path} is an existing directory name")

    @property
    def config_path(self) -> Optional[pathlib.Path]:
        return self._config_path

    @config_path.setter
    def config_path(self, new_path: pathlib.Path):
        self._config_path = new_path

    def load_config(self):
        self._check_settings_file_name()

        loaded_settings_raw = {}
        try:
            with self.config_path.open("r") as fp:
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
            except Exception:
                pass

    def save_config(self):
        self._check_settings_file_name()

        settings_dict = {}
        for item in self._registry:
            value = item.saver()
            settings_dict[item.key] = value

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with self.config_path.open("w") as fp:
            json.dump(settings_dict, fp, indent=2)
