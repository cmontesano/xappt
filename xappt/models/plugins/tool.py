from typing import Dict, Generator

from xappt.models.parameter.meta import ParamMeta
from xappt.models.parameter.model import Parameter, ParameterDescriptor
from xappt.models.plugins.base import BasePlugin


class BaseTool(BasePlugin, metaclass=ParamMeta):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._parameters_:
                param = getattr(self, key)
                param.value = value

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

    def execute(self, **kwargs) -> int:
        raise NotImplementedError
