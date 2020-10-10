import xappt


@xappt.register_plugin(visible=False)
class ExamplePlugin(xappt.BaseTool):
    arg1 = xappt.ParamString(required=True)
    arg2 = xappt.ParamString(required=True)
    arg3 = xappt.ParamString(required=True)
    arg4 = xappt.ParamList(choices=['1', '2', '3', '4'])
    arg5 = xappt.ParamBool(default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.arg5.on_value_changed.add(self._on_arg5_changed)

    def _on_arg5_changed(self, param: xappt.Parameter):
        if param.value:
            self.arg4.choices = ['5', '6', '7', '8']
        else:
            self.arg4.choices = ['1', '2', '3', '4']

    @classmethod
    def name(cls) -> str:
        return "example"

    @classmethod
    def help(cls) -> str:
        return "A simple command that will just echo the passed in arguments"

    def execute(self, interface: xappt.BaseInterface, **kwargs) -> int:
        interface.message(self.arg1.value)
        interface.message(self.arg2.value)
        interface.message(self.arg3.value)
        interface.message(self.arg4.value)
        interface.message(self.arg5.value)
        return 0
