from __future__ import annotations
import abc

from typing import TYPE_CHECKING

from xappt.models.plugins.base import BasePlugin
if TYPE_CHECKING:
    from xappt.models.plugins.tool import BaseTool


class BaseInterface(BasePlugin, metaclass=abc.ABCMeta):
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
    def error(self, message: str):
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
