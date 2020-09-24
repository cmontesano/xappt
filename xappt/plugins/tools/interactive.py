import time

import xappt


@xappt.register_plugin
class Interactive1(xappt.BaseTool):
    param1 = xappt.ParamInt(required=True)

    def execute(self, **kwargs) -> int:
        iface = kwargs['interface']
        if iface is None:
            iface_class = xappt.get_default_interface()
            iface = iface_class()

        iface.progress_start()

        for i in range(1, 101):
            iface.progress_update(f"Tests are fun: i == {i}", i / 100.0)
            time.sleep(0.05)

        iface.progress_end()

        iface.message("progress ended")

        try:
            if iface.ask("Enter more input?"):
                result = iface.invoke(Interactive2(), interface=iface, **self.param_dict())
            else:
                iface.message("Aborting")
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

    def execute(self, **kwargs) -> int:
        print(f"Got {self.param1.value}, {self.param2.value}, {self.param3.value}, "
              f"{self.param4.choices[self.param4.value]}")
        return 0
