from __future__ import annotations
import abc

from typing import Any, Optional, Sequence, Type, TYPE_CHECKING, Union

import xappt.managers.plugin_manager
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
        self.on_tool_chain_modified = Callback()

        self._current_tool_index: int = -1
        self._tool_chain: list[Type[BaseTool]] = []

        self.tool_data: dict[str: Any] = {}  # tool_data will be sent to both BaseTool.__init__ and BaseTool.execute

    @property
    def current_tool_index(self) -> int:
        return self._current_tool_index

    @property
    def tool_count(self) -> int:
        return len(self._tool_chain)

    def add_tool(self, tool_plugin: Union[str, Type[BaseTool]]):
        if isinstance(tool_plugin, str):
            tool_plugin = xappt.managers.plugin_manager.get_tool_plugin(tool_plugin)
        self._tool_chain.append(tool_plugin)
        self.on_tool_chain_modified.invoke()

    def clear_tool_chain(self):
        self._tool_chain.clear()
        self.on_tool_chain_modified.invoke()

    def get_tool(self, index: int) -> Type[BaseTool]:
        return self._tool_chain[index]

    @abc.abstractmethod
    def run(self, **kwargs) -> int:
        for i, tool_class in enumerate(self._tool_chain):
            self._current_tool_index = i
            tool_instance = tool_class(interface=self, **self.tool_data)
            result = self.invoke(tool_instance, **self.tool_data)
            if result != 0:
                return result
        return 0

    @classmethod
    def collection(cls) -> str:
        return "interface"

    @abc.abstractmethod
    def invoke(self, plugin: BaseTool, **kwargs) -> int:
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
