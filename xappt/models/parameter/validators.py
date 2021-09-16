""" All validation routines should do some basic sanity checking and return
either the original value or a sensibly massaged version of the value.

For example, with ParamInt you can specify a set of string choices. If a string is
passed to the int's validate method it should be checked against the choices,
and the index of that choice should be returned rather than the original string.
"""

import os
import re
from typing import Any, List

import xappt

from xappt.constants import TRUTHY_STRINGS

from xappt.models.parameter.model import Parameter
from xappt.models.parameter.errors import ParameterValidationError

__all__ = [
    'BaseValidator',
    'ValidateRange',
    'ValidateType',
    'ValidateChoiceInt',
    'ValidateChoiceStr',
    'ValidateDefault',
    'ValidateRequired',
    'ValidateDefaultInt',
    'ValidateBoolFromString',
    'ValidateChoiceList',
    'ValidateTypeList',
    'ValidateFileExists',
    'ValidateFolderExists',
]

NUMERIC_PATTERN = r"-?\d+(?:\.\d+)?"
BOOL_RE = re.compile(rf"^({'|'.join((NUMERIC_PATTERN, ) + TRUTHY_STRINGS)})$", re.I)


class BaseValidator:
    def __init__(self, param: Parameter):
        self.param = param

    def validate(self, value: Any) -> Any:
        raise NotImplementedError


class ValidateRequired(BaseValidator):
    def validate(self, value: Any) -> Any:
        if value is None and self.param.required:
            raise ParameterValidationError(f"Missing required parameter {self.param.name}")
        return value


class ValidateType(BaseValidator):
    def validate(self, value: Any) -> Any:
        try:
            return self.param.data_type(value)
        except BaseException as e:
            raise ParameterValidationError(str(e))


class ValidateDefault(BaseValidator):
    def validate(self, value: Any) -> Any:
        if value is None and self.param.default is not None:
            return self.param.default
        return value


class ValidateDefaultInt(BaseValidator):
    def validate(self, value: Any) -> Any:
        if value is None and self.param.default is not None:
            if self.param.choices is not None:
                return self.param.choices[self.param.default]
            else:
                return self.param.default
        return value


class ValidateRange(BaseValidator):
    def __init__(self,  param: Parameter, minimum: Any, maximum: Any):
        super().__init__(param)
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, value: Any) -> Any:
        if self.minimum is not None and value < self.minimum:
            raise ParameterValidationError(f"Value must be at least {self.minimum}")
        if self.maximum is not None and value > self.maximum:
            raise ParameterValidationError(f"Value must be at most {self.maximum}")
        return value


class ValidateChoiceInt(BaseValidator):
    def validate(self, value: Any) -> int:
        if self.param.choices is not None:
            if isinstance(value, str):
                if value not in self.param.choices:
                    raise ParameterValidationError(f"Value must be one of {xappt.humanize_list(self.param.choices)}")
                value = self.param.choices.index(value)
            elif isinstance(value, int):
                if value < 0 or value >= len(self.param.choices):
                    raise ParameterValidationError("Value does not correspond to a valid index")
        try:
            return int(value)
        except BaseException as e:
            raise ParameterValidationError(str(e))


class ValidateChoiceStr(BaseValidator):
    def validate(self, value: Any) -> str:
        if self.param.choices is not None:
            if value not in self.param.choices:
                raise ParameterValidationError(f"Value must be one of {xappt.humanize_list(self.param.choices)}")
        return value


class ValidateBoolFromString(BaseValidator):
    def validate(self, value: Any) -> bool:
        if isinstance(value, str):
            return BOOL_RE.match(value) is not None
        return value


class ValidateChoiceList(BaseValidator):
    def validate(self, value: Any) -> List[str]:
        if self.param.choices is not None:
            for item in value:
                if item not in self.param.choices:
                    raise ParameterValidationError(f"Value must be one of {xappt.humanize_list(self.param.choices)}")
        return value


class ValidateTypeList(BaseValidator):
    def validate(self, value: Any) -> Any:
        if isinstance(value, str):
            value = value.split(";")
        return self.param.data_type(value)


class ValidateFolderExists(BaseValidator):
    def validate(self, value: str) -> str:
        value = os.path.abspath(value)
        if not os.path.isdir(value):
            raise xappt.ParameterValidationError(f"Path '{value}' does not exist.")
        return value


class ValidateFileExists(BaseValidator):
    def validate(self, value: str) -> str:
        value = os.path.abspath(value)
        if not os.path.isfile(value):
            raise xappt.ParameterValidationError(f"File '{value}' does not exist.")
        return value
