from __future__ import annotations

from typing import Dict, Generator, TYPE_CHECKING

from xappt.models.parameter.meta import ParamMeta
from xappt.models.parameter.model import Parameter, ParameterDescriptor
from xappt.models.plugins.base import BasePlugin
if TYPE_CHECKING:
    from xappt.models.plugins.interface import BaseInterface


class BaseTool(BasePlugin, metaclass=ParamMeta):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._parameters_:
                param = getattr(self, key)
                param.value = param.validate(value)

    @classmethod
    def collection(cls) -> str:
        return "tool"

    @classmethod
    def class_parameters(cls) -> Generator[ParameterDescriptor, None, None]:
        for item in cls._parameters_:
            yield getattr(cls, item)

    def parameters(self) -> Generator[Parameter, None, None]:
        for item in self._parameters_:
            yield getattr(self, item)

    def param_dict(self) -> Dict:
        d = {}
        for p in self.parameters():
            d[p.name] = p.value
        return d

    def execute(self, interface: BaseInterface, **kwargs) -> int:
        raise NotImplementedError

    def validate(self):
        for param in self.parameters():
            param.validate(param.value)
