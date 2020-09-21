import copy
from typing import Type


__all__ = [
    "ParamMeta",
    "Parameter",
    "ParamString",
    "ParamBool",
    "ParamInt",
    "ParamFloat",
]


class Parameter:
    def __init__(self, name: str, *, data_type: Type, **kwargs):
        self.name = name
        self.data_type = data_type
        self.description = kwargs['description']
        self.value = kwargs['value']
        self.required = kwargs['required']


class ParameterDescriptor:
    __counter = 0

    default_values = {
        'required': False,
        'description': "",
        'short_name': None,
    }

    def __init__(self, data_type: Type, **kwargs):
        cls = self.__class__
        self.storage_name = '_{}#{}'.format(cls.__name__, cls.__counter)
        kwargs['data_type'] = data_type
        kwargs['default'] = kwargs.get('default', data_type())
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


class ParamMeta(type):
    def __new__(mcs, name, bases, attrs):
        cls = type.__new__(mcs, name, bases, attrs)
        cls._parameters_ = []
        for var_name, var_value in vars(cls).items():
            if isinstance(var_value, ParameterDescriptor):
                cls._parameters_.append(var_name)
                var_value.param_setup_args['name'] = var_name
        return cls


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
