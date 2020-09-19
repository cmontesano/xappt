import argparse
import os

from xappt.utilities import git_tools

from xappt.models import Plugin
from xappt.managers.plugin_manager import register_plugin


@register_plugin(active=True)
class SelfCheck(Plugin):
    def __init__(self):
        super().__init__()
        repo_path_default = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self._repository_path = os.environ.get('XAPPT_ROOT', repo_path_default)

    @classmethod
    def build_parser(cls, parser: argparse.ArgumentParser):
        pass

    def _is_modified(self) -> bool:
        if git_tools.is_dirty(self._repository_path):
            print("Changes were detected")
            return True

        print("No changes detected")
        return False

    def execute(self, **kwargs) -> int:
        return int(self._is_modified())
