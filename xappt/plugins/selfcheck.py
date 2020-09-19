import argparse
import os

from xappt.utilities import CommandRunner

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
        cmd = CommandRunner(cwd=self._repository_path)

        # are we a git repository?
        result = cmd.run(("git", "rev-parse", "HEAD"))
        if result.result != 0:
            print("Xappt is not running from a git repository")
            return True

        cmd.run(("git", "fetch", "origin"))

        # check for remote change
        result = cmd.run(("git", "diff", "--quiet", "master", "origin/master"))
        if result.result != 0:
            print("Remote changes detected")
            return True

        # check for local change
        result = cmd.run(("git", "diff-index", "--quiet", "HEAD", "--"))
        if result.result != 0:
            print("Local changes detected")
            return True

        print("No changes detected")
        return False

    def execute(self, **kwargs) -> int:
        return int(self._is_modified())
