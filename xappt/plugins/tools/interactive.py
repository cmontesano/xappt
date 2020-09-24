import time

import xappt


@xappt.register_plugin
class Interactive1(xappt.BaseTool):
    param1 = xappt.ParamInt(required=True)

    def execute(self, interface: xappt.BaseInterface, **kwargs) -> int:
        if interface is None:
            iface_class = xappt.get_default_interface()
            interface = iface_class()

        interface.progress_start()

        for i in range(1, 101):
            interface.progress_update(f"Tests are fun: i == {i}", i / 100.0)
            time.sleep(0.05)

        interface.progress_end()

        interface.message("progress ended")

        try:
            if interface.ask("Enter more input?"):
                result = interface.invoke(Interactive2(), **self.param_dict())
            else:
                interface.message("Aborting")
                result = 0
        except KeyboardInterrupt:
            result = 1
        return result


@xappt.register_plugin(visible=False)
class Interactive2(xappt.BaseTool):
    param1 = xappt.ParamInt(description="A number between 1 and 10, inclusive", minimum=1, maximum=10)
    param2 = xappt.ParamInt(description="A number between 10 and 20, inclusive", minimum=10, maximum=20)
    param3 = xappt.ParamInt(default=7, description="Any integer")
    param4 = xappt.ParamInt(description="Run silently?", choices=("y", "n"), default=0)

    def execute(self, interface: xappt.BaseInterface, **kwargs) -> int:
        print(f"Got {self.param1.value}, {self.param2.value}, {self.param3.value}, "
              f"{self.param4.choices[self.param4.value]}")
        return 0
