import os

from xappt.utilities import git_tools

from xappt.models import *
from xappt.managers.plugin_manager import register_plugin


@register_plugin(active=True)
class SelfCheck(Plugin):
    @classmethod
    def help(cls) -> str:
        return "If running from a cloned copy of the git repository, check to see if the " \
               "code being run matches the remote."

    @staticmethod
    def _is_modified() -> bool:
        _repository_path = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
        if git_tools.is_dirty(_repository_path):
            print("Changes were detected or not a repository")
            return True

        print("No changes detected")
        return False

    def execute(self) -> int:
        return int(self._is_modified())
