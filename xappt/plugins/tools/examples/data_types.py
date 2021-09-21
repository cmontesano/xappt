import pprint
import time

import xappt


@xappt.register_plugin
class DataTypes(xappt.BaseTool):
    integer_choice = xappt.ParamInt(description="Choose an item", choices=("apple", "banana", "cantaloupe"))
    integer_range = xappt.ParamInt(description="A number between 1 and 20, inclusive", minimum=1, maximum=20, default=1)
    hidden_parameter = xappt.ParamInt(description="Any integer", hidden=True, default=7)
    boolean_check = xappt.ParamBool(description="Toggle me")
    string_field = xappt.ParamString(description="Enter any text")
    string_choice = xappt.ParamString(description="Choose an item", choices=("red", "green", "blue"))
    list_choice = xappt.ParamList(description="Choose multiple items", choices=("first", "second", "third", "fourth"))

    @classmethod
    def help(cls) -> str:
        return "An example of the various parameter data types"

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def execute(self, **kwargs) -> int:
        self.interface.progress_start()
        for i in range(1, 101):
            self.interface.progress_update(f"Working {i}%", i / 100.0)
            time.sleep(0.01)
        self.interface.progress_end()

        param_dict_string = pprint.pformat(self.param_dict(), indent=2, sort_dicts=False)
        self.interface.message(param_dict_string)

        return 0
