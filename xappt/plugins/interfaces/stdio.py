from typing import Any, Callable, Dict, Sequence, Type

import xappt

from xappt.models.parameter.model import Parameter


@xappt.register_plugin
class StdIO(xappt.BaseInterface):
    def __init__(self):
        super().__init__()

        self.validation_dispatch: Dict[Type, Callable] = {
            int: self.check_int,
        }

        self.prompt_dispatch: Dict[Type, Callable] = {
            int: self.prompt_int,
        }

    def invoke(self, plugin: xappt.BaseTool, **kwargs):
        for param in plugin.parameters():
            self.prompt_for_param(param)
        return plugin.execute(**kwargs)

    def check_default(self, param: Parameter, value: Any):
        if value is None and param.default is not None:
            value = param.default
        return value

    def check_int(self, param: Parameter, value: Any):
        if param.choices is not None:
            if value is None and param.default is not None:
                value = param.choices[param.default]
            if value not in param.choices:
                raise ValueError(f"Value must be one of {xappt.humanize_list(param.choices)}")
            value = param.choices.index(value)
        else:
            if value is None and param.default is not None:
                value = param.default
            value = int(value)
            minimum = param.options.get('min')
            if minimum is not None and value < minimum:
                raise ValueError(f"Value must be at least {minimum}")
            maximum = param.options.get('max')
            if maximum is not None and value > maximum:
                raise ValueError(f"Value must be less than {maximum}")
        return value

    def prompt_default(self, param: Parameter) -> str:
        if param.default is not None:
            return f"{param.name} ({param.default}): "
        return f"{param.name}: "

    def prompt_int(self, param: Parameter) -> str:
        if param.choices is not None:
            if param.default is not None:
                choice_values = []
                for i, value in enumerate(param.choices):
                    if i == param.default:
                        choice_values.append(f'{value}*')
                    else:
                        choice_values.append(value)
            else:
                choice_values = param.choices
            return f"{param.name} ({'|'.join(choice_values)}): "
        return self.prompt_default(param)

    def prompt_for_param(self, param: Parameter):
        prompt_fn = self.prompt_dispatch.get(param.data_type, self.prompt_default)
        validation_fn = self.validation_dispatch.get(param.data_type, self.check_default)
        prompt = prompt_fn(param)

        print("")
        if len(param.description):
            print(param.description)

        while True:
            value = input(prompt)
            if len(value) == 0:
                value = None
            try:
                value = validation_fn(param, value)
            except BaseException as e:
                print(f"Error: {e}")
                print("Try again")
                print("")
            else:
                break

        param.value = value
