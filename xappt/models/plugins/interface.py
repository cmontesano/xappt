from __future__ import annotations
import abc

from collections import defaultdict
from typing import Callable, DefaultDict, Optional, Sequence, Set, TYPE_CHECKING, Union

from xappt.utilities.command_runner import CommandRunner

from xappt.models.plugins.base import BasePlugin
if TYPE_CHECKING:
    from xappt.models.plugins.tool import BaseTool


class BaseInterface(BasePlugin, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.command_runner = CommandRunner()
        self._callbacks: DefaultDict[str, Set[Optional[Callable]]] = defaultdict(set)

    @classmethod
    def collection(cls) -> str:
        return "interface"

    @abc.abstractmethod
    def invoke(self, plugin: BaseTool, **kwargs):
        pass

    @abc.abstractmethod
    def message(self, message: str):
        pass

    @abc.abstractmethod
    def warning(self, message: str):
        pass

    @abc.abstractmethod
    def error(self, message: str, *, details: Optional[str] = None):
        pass

    @abc.abstractmethod
    def ask(self, message: str) -> bool:
        pass

    @abc.abstractmethod
    def progress_start(self):
        pass

    @abc.abstractmethod
    def progress_update(self, message: str, percent_complete: float):
        pass

    @abc.abstractmethod
    def progress_end(self):
        pass

    def add_stdout_callback(self, stdout_fn):
        self._callbacks['stdout'].add(stdout_fn)

    def add_stderr_callback(self, stderr_fn):
        self._callbacks['stderr'].add(stderr_fn)

    def write_stdout(self, text: str):
        for callback in self._callbacks['stdout']:
            callback(text)

    def write_stderr(self, text: str):
        for callback in self._callbacks['stderr']:
            callback(text)

    def run_subprocess(self, command: Union[bytes, str, Sequence]) -> int:
        result = self.command_runner.run(command, stdout_fn=self.write_stdout, stderr_fn=self.write_stderr)
        return result.result
