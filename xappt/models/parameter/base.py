from typing import Generator

from xappt.models.parameter.meta import ParamMeta
from xappt.models.parameter.model import Parameter, ParamSetupDict, ParameterDescriptor
from xappt.models.parameter.errors import ParameterValidationError
from xappt.models.plugins.base import BasePlugin


class BaseParameterPlugin(BasePlugin, metaclass=ParamMeta):
    def __init__(self, **kwargs):
        super().__init__()
        for param_name in self._parameters_:
            param: Parameter = getattr(self, param_name)
            if param_name in kwargs:
                param_value = kwargs[param_name]
                if isinstance(param_value, ParamSetupDict):
                    param.update(param_value)
                elif param_value is None:
                    pass  # leave this parameter's value empty
                else:
                    param._value = param.validate(param_value)
            else:
                try:
                    param._value = param.validate(param.value)
                except ParameterValidationError:
                    # run validations, but don't raise validation errors
                    pass

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
