import argparse

from typing import Generator

from xappt.models.parameter.meta import ParamMeta
from xappt.models.parameter.model import Parameter

SubParser = type(argparse.ArgumentParser().add_subparsers())


class Plugin(metaclass=ParamMeta):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._parameters_:
                param = getattr(self, key)
                param.value = value

    @classmethod
    def class_parameters(cls) -> Generator[Parameter, None, None]:
        for item in cls._parameters_:
            yield getattr(cls, item)

    def parameters(self) -> Generator[Parameter, None, None]:
        for item in self._parameters_:
            yield getattr(self, item)

    @classmethod
    def name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def help(cls) -> str:
        return ""

    def execute(self) -> int:
        raise NotImplementedError
