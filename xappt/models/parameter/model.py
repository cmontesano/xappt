from __future__ import annotations

import copy

from collections import defaultdict

from typing import Any, Callable, Dict, DefaultDict, List, Optional, Sequence, Set, Tuple, Type
from typing import TYPE_CHECKING

from xappt.models.callback import Callback
if TYPE_CHECKING:
    from xappt.models.parameter.validators import BaseValidator


class Parameter:
    def __init__(self, name: str, *, data_type: Type, **kwargs):
        self.name: str = name
        self.data_type: Type = data_type
        self.description: str = kwargs.get('description', "")
        self.default: Any = kwargs['default']
        self.required: bool = kwargs['required']
        self._choices: Optional[Sequence] = kwargs.get('choices')
        self._options: Dict[str: Any] = kwargs.get('options', {})
        self.validators: List[BaseValidator] = []
        self._value = kwargs['value']
        self.metadata: Dict = kwargs.get('metadata', {})

        for validator in kwargs.get('validators', []):
            if isinstance(validator, Tuple):
                validator, *args = validator
            else:
                args = []
            self.validators.append(validator(self, *args))

        self.on_value_changed = Callback()
        self.on_choices_changed = Callback()
        self.on_options_changed = Callback()

    def validate(self, value: Any) -> Any:
        for validator in self.validators:
            value = validator.validate(value)
        return value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.on_value_changed.invoke(param=self)

    @property
    def choices(self) -> Optional[Sequence]:
        return self._choices

    @choices.setter
    def choices(self, new_choices: Optional[Sequence]):
        self._choices = new_choices
        self.on_choices_changed.invoke(param=self)

    @property
    def options(self) -> Dict:
        return self._options

    def option(self, key: str, default: Any) -> Any:
        return self._options.get(key, default)

    def set_option(self, key: str, value: Any):
        self._options[key] = value
        self.on_options_changed.invoke(param=self)


class ParameterDescriptor:
    __counter = 0

    def __init__(self, data_type: Type, **kwargs):
        cls = self.__class__
        self.storage_name = '_{}#{}'.format(cls.__name__, cls.__counter)
        kwargs['data_type'] = data_type
        if 'default' not in kwargs:
            kwargs['required'] = True
        else:
            kwargs['required'] = False
        kwargs['default'] = kwargs.get('default')
        kwargs['value'] = kwargs.get('value', kwargs['default'])
        if "description" not in kwargs:
            kwargs['description'] = ""
        self.param_setup_args = copy.deepcopy(kwargs)
        cls.__counter += 1

    def get_parameter(self, instance):
        param = getattr(instance, self.storage_name, None)
        if param is None:
            # Create new parameter instance of descriptor properties
            param = Parameter(**self.param_setup_args)
            setattr(instance, self.storage_name, param)
            return param
        return param

    def __get__(self, instance, owner):
        if instance is None:
            # Call was not through an instance
            return self
        else:
            return self.get_parameter(instance)

    def __set__(self, instance, value):
        raise AttributeError("Parameter is read only. Use Parameter's value attribute")
