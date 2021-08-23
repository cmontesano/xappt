from .model import ParameterDescriptor


class ParamMeta(type):
    def __new__(mcs, name, bases, attrs):
        cls = type.__new__(mcs, name, bases, attrs)
        base_parameters = []
        for base in bases:
            try:
                base_parameters += base._parameters_  # noqa
            except AttributeError:
                pass
        cls._parameters_ = base_parameters
        for var_name, var_value in vars(cls).items():
            if isinstance(var_value, ParameterDescriptor):
                try:
                    _ = cls._parameters_.index(var_name)
                except ValueError:
                    cls._parameters_.append(var_name)
                var_value.param_setup_args['name'] = var_name
        return cls
