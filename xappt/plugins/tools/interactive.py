import xappt


@xappt.register_plugin
class Interactive1(xappt.BaseTool):
    param1 = xappt.ParamInt(required=True)

    def execute(self, **kwargs) -> int:
        iface_class = xappt.get_default_interface()
        iface = iface_class()
        try:
            result = iface.invoke(Interactive2(), **self.param_dict())
        except KeyboardInterrupt:
            result = 1
        return result


@xappt.register_plugin(visible=False)
class Interactive2(xappt.BaseTool):
    param1 = xappt.ParamInt(description="A number between 1 and 10, inclusive", minimum=1, maximum=10)
    param2 = xappt.ParamInt(description="A number between 10 and 20, inclusive", minimum=10, maximum=20)
    param3 = xappt.ParamInt(default=7, description="Any integer")
    param4 = xappt.ParamInt(description="Run silently?", choices=("y", "n"), default=0)

    def execute(self, **kwargs) -> int:
        print(f"Got {self.param1.value}, {self.param2.value}, {self.param3.value}, "
              f"{self.param4.choices[self.param4.value]}")
        return 0
