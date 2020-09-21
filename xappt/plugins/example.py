from xappt.models import *
from xappt.managers.plugin_manager import register_plugin


@register_plugin
class ExamplePlugin(Plugin):
    arg1 = ParamString(required=True)
    arg2 = ParamString(required=True)
    arg3 = ParamString(required=True)

    @classmethod
    def name(cls) -> str:
        return "example"

    @classmethod
    def help(cls) -> str:
        return "A simple command that will just echo the passed in arguments"

    def execute(self) -> int:
        print(self.arg1.value)
        print(self.arg2.value)
        print(self.arg3.value)
        return 0
