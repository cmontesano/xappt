from typing import Optional, Sequence

from .model import ParameterDescriptor


__all__ = [
    'ParamString',
    'ParamBool',
    'ParamInt',
    'ParamFloat',
]


class ParamString(ParameterDescriptor):
    def __init__(self, **kwargs):
        super().__init__(data_type=str, **kwargs)


class ParamBool(ParameterDescriptor):
    def __init__(self, **kwargs):
        super().__init__(data_type=bool, **kwargs)


class ParamInt(ParameterDescriptor):
    def __init__(self, *, minimum: Optional[int] = None, maximum: Optional[int] = None,
                 choices: Optional[Sequence] = None, **kwargs):
        super().__init__(data_type=int, minimum=minimum, maximum=maximum, choices=choices, **kwargs)


class ParamFloat(ParameterDescriptor):
    def __init__(self, **kwargs):
        super().__init__(data_type=float, **kwargs)
