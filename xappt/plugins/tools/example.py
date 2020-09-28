import xappt


@xappt.register_plugin
class ExamplePlugin(xappt.BaseTool):
    arg1 = xappt.ParamString(required=True)
    arg2 = xappt.ParamString(required=True)
    arg3 = xappt.ParamString(required=True)

    @classmethod
    def name(cls) -> str:
        return "example"

    @classmethod
    def help(cls) -> str:
        return "A simple command that will just echo the passed in arguments"

    def execute(self, **kwargs) -> int:
        print(self.arg1.value)
        print(self.arg2.value)
        print(self.arg3.value)
        return 0
