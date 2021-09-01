from typing import Generator

from xappt.models.parameter.meta import ParamMeta
from xappt.models.parameter.model import Parameter, ParamSetupDict, ParameterDescriptor


class BaseParameter(metaclass=ParamMeta):
    def __init__(self, **kwargs):
        super().__init__()
        for param_name in self._parameters_:
            param: Parameter = getattr(self, param_name)
            if param_name in kwargs:
                param_value = kwargs[param_name]
                if isinstance(param_value, ParamSetupDict):
                    param.update(param_value)
                else:
                    param._value = param.validate(param_value)
            else:
                param._value = param.validate(param.value)

    @classmethod
    def class_parameters(cls) -> Generator[ParameterDescriptor, None, None]:
        for item in cls._parameters_:
            yield getattr(cls, item)

    def parameters(self) -> Generator[Parameter, None, None]:
        for item in self._parameters_:
            yield getattr(self, item)

    def param_dict(self) -> dict:
        d = {}
        for p in self.parameters():
            d[p.name] = p.value
        return d

    def validate(self):
        for param in self.parameters():
            param.validate(param.value)