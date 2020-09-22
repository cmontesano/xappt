import xappt

from xappt.models.parameter.model import Parameter


@xappt.register_plugin
class StdIO(xappt.BaseInterface):
    def invoke(self, plugin: xappt.BaseTool, **kwargs):
        for param in plugin.parameters():
            self.prompt_for_param(param)
        return plugin.execute(**kwargs)

    @staticmethod
    def prompt_for_param(param: Parameter):
        if param.default is not None:
            prompt = f"{param.name} ({param.default}): "
        else:
            prompt = f"{param.name}: "
        if len(param.description):
            print(param.description)

        while True:
            value = input(prompt)
            if len(value) == 0 and param.default is not None:
                value = param.default
            try:
                value = param.data_type(value)
            except BaseException as e:
                print(f"Error: {e}")
                print("Try again")
                print("")
            else:
                break

        param.value = value
