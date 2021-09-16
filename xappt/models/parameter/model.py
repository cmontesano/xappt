from __future__ import annotations

from typing import Any, Optional, Sequence, Type
from typing import TYPE_CHECKING

from xappt.models.callback import Callback
if TYPE_CHECKING:
    from xappt.models.parameter.validators import BaseValidator


class ParamSetupDict(dict):
    def __init__(self, default=None, required=None, choices=None, options=None, value=None,
                 metadata=None, hidden=None, **kwargs):
        kwargs['default'] = default
        kwargs['required'] = required
        kwargs['choices'] = choices
        kwargs['options'] = options or {}
        kwargs['value'] = value
        kwargs['metadata'] = metadata or {}
        kwargs['hidden'] = hidden or False
        super(ParamSetupDict, self).__init__(**kwargs)


class Parameter:
    def __init__(self, name: str, *, data_type: Type, **kwargs):
        self.name: str = name
        self.data_type: Type = data_type
        self.description: str = kwargs.get('description', "")
        self.default: Any = kwargs['default'] or data_type()
        self.required: bool = kwargs['required']
        self._choices: Optional[Sequence] = kwargs.get('choices')
        self._options: dict[str: Any] = kwargs.get('options', {})
        self.validators: list[BaseValidator] = []
        self._value = kwargs['value']
        self.metadata: dict = kwargs.get('metadata', {})
        self._hidden: bool = kwargs.get('hidden', False)

        for validator in kwargs.get('validators', []):
            if isinstance(validator, tuple):
                validator, *args = validator
            else:
                args = []
            self.validators.append(validator(self, *args))

        self.on_value_changed = Callback()
        self.on_choices_changed = Callback()
        self.on_options_changed = Callback()
        self.on_visibility_changed = Callback()

    def update(self, update_args: ParamSetupDict):
        self.default = update_args.get('default', self.default)
        self.required = update_args.get('required', self.required)
        self._choices = update_args.get('choices', self._choices)
        self._options.update(update_args.get('options', {}))
        self._value = self.validate(update_args.get('value', self.value))
        self.metadata.update(update_args.get('metadata', {}))

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
        if self.data_type is str:
            if self.default is not None and self.default not in self._choices:
                self.default = self._choices[0]
            if self._value not in self._choices:
                self._value = self.default
        elif self.data_type is int:
            if self.default < 0 or self.default >= len(self._choices):
                self.default = 0
            if self._value < 0 or self._value >= len(self._choices):
                self._value = self.default
        self.on_choices_changed.invoke(param=self)

    @property
    def options(self) -> dict:
        return self._options

    def option(self, key: str, default: Any) -> Any:
        return self._options.get(key, default)

    def set_option(self, key: str, value: Any):
        self._options[key] = value
        self.on_options_changed.invoke(param=self)

    @property
    def hidden(self):  # read only
        return self._hidden

    @hidden.setter
    def hidden(self, new_hidden: bool):
        self._hidden = new_hidden
        self.on_visibility_changed.invoke(param=self)


class ParameterDescriptor:
    __counter = 0

    def __init__(self, data_type: Type, **kwargs):
        cls = self.__class__
        self.storage_name = f"_{cls.__name__}#{cls.__counter}"

        self.param_setup_args = ParamSetupDict(**kwargs)
        self.param_setup_args['data_type'] = data_type

        if "description" not in kwargs:
            self.param_setup_args['description'] = ""

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
