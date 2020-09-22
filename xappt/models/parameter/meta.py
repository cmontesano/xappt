from .model import ParameterDescriptor


class ParamMeta(type):
    def __new__(mcs, name, bases, attrs):
        cls = type.__new__(mcs, name, bases, attrs)
        cls._parameters_ = []
        for var_name, var_value in vars(cls).items():
            if isinstance(var_value, ParameterDescriptor):
                cls._parameters_.append(var_name)
                var_value.param_setup_args['name'] = var_name
        return cls
