from typing import Optional, Sequence

from xappt.models.parameter.model import ParameterDescriptor
from xappt.models.parameter.validators import *


__all__ = [
    'ParamString',
    'ParamBool',
    'ParamInt',
    'ParamFloat',
]


class ParamString(ParameterDescriptor):
    def __init__(self, *, choices: Optional[Sequence[str]] = None, **kwargs):
        validators = [
            ValidateDefault,
            ValidateType,
            ValidateChoiceStr,
        ] + kwargs.get('validators', [])
        kwargs['validators'] = validators
        super().__init__(data_type=str, choices=choices, **kwargs)


class ParamBool(ParameterDescriptor):
    def __init__(self, **kwargs):
        validators = [
            ValidateBoolFromString,
            ValidateDefault,
            ValidateType,
        ] + kwargs.get('validators', [])
        kwargs['validators'] = validators
        super().__init__(data_type=bool, **kwargs)


class ParamInt(ParameterDescriptor):
    def __init__(self, *, minimum: Optional[int] = None, maximum: Optional[int] = None,
                 choices: Optional[Sequence[str]] = None, **kwargs):
        validators = [
            ValidateDefaultInt,
            ValidateChoiceInt,
            (ValidateRange, minimum, maximum),
        ] + kwargs.get('validators', [])
        kwargs['validators'] = validators
        super().__init__(data_type=int, choices=choices, **kwargs)


class ParamFloat(ParameterDescriptor):
    def __init__(self, *, minimum: Optional[float] = None, maximum: Optional[float] = None, **kwargs):
        validators = [
            ValidateDefault,
            ValidateType,
            (ValidateRange, minimum, maximum),
        ] + kwargs.get('validators', [])
        kwargs['validators'] = validators
        super().__init__(data_type=float, **kwargs)
