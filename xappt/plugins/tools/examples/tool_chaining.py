import xappt

TOOL_CHOICES = {
    "data types": "datatypes",
    "modify choices": "modifychoices",
    "none (quit)": None,
}


@xappt.register_plugin
class ToolChaining(xappt.BaseTool):
    next_tool = xappt.ParamString(description="Choose the next task", choices=list(TOOL_CHOICES.keys()))
    persistent_data = xappt.ParamString(description="This value should persist between tools")

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
        interface.tool_data['persistent_data'] = self.persistent_data.value

        first_run = kwargs.get('first_run', True)
        if first_run:
            interface.write_stdout("Any queued tools will be initialized with the contents of `interface.tool_data`.")
            interface.write_stdout("`interface.tool_data` will also be passed to `BaseTool.execute` as **kwargs.")
            interface.write_stdout("This can be used not only to initialize subsequent")
            interface.tool_data['first_run'] = False

        next_tool_name = TOOL_CHOICES[self.next_tool.value]
        if next_tool_name is not None:
            interface.add_tool(next_tool_name)
            interface.add_tool(ToolChaining)  # return here after the other tool runs

        return 0
