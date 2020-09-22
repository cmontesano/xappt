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
    def __init__(self, **kwargs):
        super().__init__(data_type=int, **kwargs)


class ParamFloat(ParameterDescriptor):
    def __init__(self, **kwargs):
        super().__init__(data_type=float, **kwargs)
