import xappt


@xappt.register_plugin
class Interactive1(xappt.BaseTool):
    param1 = xappt.ParamInt(required=True)

    def execute(self, **kwargs) -> int:
        iface_class = xappt.get_default_interface()
        iface = iface_class()
        return iface.invoke(Interactive2(), **self.param_dict())


@xappt.register_plugin(visible=False)
class Interactive2(xappt.BaseTool):
    param1 = xappt.ParamInt(description="test1")
    param2 = xappt.ParamInt(description="test2")
    param3 = xappt.ParamInt(default=7, description="test3")

    def execute(self, **kwargs) -> int:
        print(f"Got {self.param1.value}, {self.param2.value}, {self.param3.value}")
        return 0
