import copy

from typing import Type


class Parameter:
    def __init__(self, name: str, *, data_type: Type, **kwargs):
        self.name = name
        self.data_type = data_type
        self.description = kwargs['description']
        self.default = kwargs['default']
        self.value = kwargs['value']
        self.required = kwargs['required']
        self.minimum = kwargs.get('minimum')
        self.maximum = kwargs.get('maximum')
        self.choices = kwargs.get('choices')
        self.options = kwargs.get('options', {})


class ParameterDescriptor:
    __counter = 0

    default_values = {
        'description': "",
        'short_name': None,
    }

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
        for k, v in self.default_values.items():
            if k not in kwargs:
                kwargs[k] = v
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
