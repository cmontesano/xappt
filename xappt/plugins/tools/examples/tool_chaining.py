import xappt

TOOL_CHOICES = {
    "data types": xappt.plugin_manager.get_tool_plugin("datatypes"),
    "modify choices": xappt.plugin_manager.get_tool_plugin("modifychoices"),
    "none (quit)": None,
}


@xappt.register_plugin
class ToolChaining(xappt.BaseTool):
    next_tool = xappt.ParamString(description="Choose the next task", choices=list(TOOL_CHOICES.keys()))

    @classmethod
    def name(cls) -> str:
        return "chaining-example"

    @classmethod
    def help(cls) -> str:
        return "Invoking a dynamic chain of tools"

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def execute(self, *, interface: xappt.BaseInterface, **kwargs) -> int:
        next_tool_class = TOOL_CHOICES[self.next_tool.value]
        if next_tool_class is not None:
            interface.add_tool(next_tool_class)
            interface.add_tool(ToolChaining)  # return here after the other tool
        return 0
