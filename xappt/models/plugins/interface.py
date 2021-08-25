from __future__ import annotations
import abc

from collections import defaultdict
from typing import Callable, DefaultDict, Optional, Sequence, Set, TYPE_CHECKING, Union

from xappt.utilities.command_runner import CommandRunner

from xappt.models.plugins.base import BasePlugin
from xappt.models.parameter.model import Callback
if TYPE_CHECKING:
    from xappt.models.plugins.tool import BaseTool


class BaseInterface(BasePlugin, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self):
        super().__init__()
        self.command_runner = CommandRunner()

        self.on_write_stdout = Callback()
        self.on_write_stderr = Callback()

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

    def write_stdout(self, text: str):
        self.on_write_stdout.invoke(text)

    def write_stderr(self, text: str):
        self.on_write_stderr.invoke(text)

    def run_subprocess(self, command: Union[bytes, str, Sequence], **kwargs) -> int:
        result = self.command_runner.run(command, stdout_fn=self.write_stdout, stderr_fn=self.write_stderr, **kwargs)
        return result.result
