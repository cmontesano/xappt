from __future__ import annotations

from typing import TYPE_CHECKING

from xappt.models.parameter.base import BaseParameterPlugin
if TYPE_CHECKING:
    from xappt.models.plugins.interface import BaseInterface


class BaseTool(BaseParameterPlugin):
    @classmethod
    def collection(cls) -> str:
        return "tool"

    def execute(self, *, interface: BaseInterface, **kwargs) -> int:
        raise NotImplementedError
