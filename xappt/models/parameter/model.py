import copy

from typing import Any, Dict, Optional, Sequence, Type


class Parameter:
    def __init__(self, name: str, *, data_type: Type, **kwargs):
        self.name: str = name
        self.data_type: Type = data_type
        self.description: str = kwargs.get('description', "")
        self.default: Any = kwargs['default']
        self.required: bool = kwargs['required']
        self.minimum: Any = kwargs.get('minimum')
        self.maximum: Any = kwargs.get('maximum')
        self.choices: Optional[Sequence] = kwargs.get('choices')
        self.options: Dict = kwargs.get('options', {})
        self.value = kwargs['value']

    def validate(self, value: Any) -> Any:
        from xappt.models.parameter.validators import validate_param
        return validate_param(self, value)


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
