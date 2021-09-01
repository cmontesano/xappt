from __future__ import annotations

from typing import TYPE_CHECKING

from xappt.models.parameter.base import BaseParameter
if TYPE_CHECKING:
    from xappt.models.plugins.interface import BaseInterface


class BaseTool(BaseParameter):
    def __init__(self, *, interface: BaseInterface, **kwargs):
        super().__init__(**kwargs)
        self._interface = interface

    @classmethod
    def collection(cls) -> str:
        return "tool"

    @property
    def interface(self) -> BaseInterface:
        return self._interface

    def execute(self, **kwargs) -> int:
        raise NotImplementedError
