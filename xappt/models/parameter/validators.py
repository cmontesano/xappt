""" All validation methods should do some basic sanity checking and return
either the original value or a sensibly massaged version of the value.

For example, with ParamInt you can specify a set of string choices. If a string is
passed to the int's validate method it should be checked against the choices,
and the index of that choice should be returned rather than the original string.
"""

from typing import Any, Callable, Dict, Type

import xappt

from xappt.models.parameter.model import Parameter
from xappt.models.parameter.errors import ParameterValidationError


def validate_type(param: Parameter, value: Any) -> Any:
    try:
        return param.data_type(value)
    except BaseException as e:
        raise ParameterValidationError(str(e))


def validate_default(param: Parameter, value: Any) -> Any:
    if value is None and param.default is not None:
        return param.default
    return value


def validate_default_int(param: Parameter, value: Any) -> Any:
    if value is None and param.default is not None:
        if param.choices is not None:
            return param.choices[param.default]
        else:
            return param.default
    return value


def validate_min_max(param: Parameter, value: Any) -> Any:
    minimum = param.minimum
    if minimum is not None and value < minimum:
        raise ParameterValidationError(f"Value must be at least {minimum}")
    maximum = param.maximum
    if maximum is not None and value > maximum:
        raise ParameterValidationError(f"Value must be at most {maximum}")
    return value


def validate_choice(param: Parameter, value: Any) -> int:
    if param.choices is not None:
        if value not in param.choices:
            raise ParameterValidationError(f"Value must be one of {xappt.humanize_list(param.choices)}")
        value = param.choices.index(value)
    return validate_type(param, value)


def validate_int(param: Parameter, value: Any) -> int:
    value = validate_default_int(param, value)
    value = validate_choice(param, value)
    value = validate_min_max(param, value)
    return value


def validate_bool(param: Parameter, value: Any) -> bool:
    value = validate_default(param, value)
    value = validate_type(param, value)
    return value


def validate_string(param: Parameter, value: Any) -> str:
    value = validate_default(param, value)
    value = validate_type(param, value)
    return value


def validate_float(param: Parameter, value: Any) -> float:
    value = validate_default(param, value)
    value = validate_type(param, value)
    value = validate_min_max(param, value)
    return value


VALIDATE_DISPATCH: Dict[Type, Callable] = {
    int: validate_int,
    bool: validate_bool,
    str: validate_string,
    float: validate_float,
}


def validate_param(param: Parameter, value: Any) -> Any:
    return VALIDATE_DISPATCH[param.data_type](param, value)
