from __future__ import annotations

from typing import TYPE_CHECKING

from xappt.models.parameter.base import BaseParameterPlugin
if TYPE_CHECKING:
    from xappt.models.plugins.interface import BaseInterface


class BaseTool(BaseParameterPlugin):
    def __init__(self, *, interface: BaseInterface, **kwargs):
        super(BaseTool, self).__init__(**kwargs)
        self.interface = interface

    @classmethod
    def collection(cls) -> str:
        return "tool"

    def execute(self, **kwargs) -> int:
        raise NotImplementedError
