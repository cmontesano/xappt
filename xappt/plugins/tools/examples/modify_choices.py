import xappt


ITEM_MAP = {
    "first": ("apple", "banana", "cantaloupe"),
    "second": ("red", "green", "blue"),
    "third": ("alpha", "beta", "gamma"),
}


@xappt.register_plugin
class ModifyChoices(xappt.BaseTool):
    integer_choice = xappt.ParamInt(description="Choose an item", choices=list(ITEM_MAP.keys()))
    string_choice = xappt.ParamString(description="Choose an item", choices=ITEM_MAP['first'])

    @classmethod
    def help(cls) -> str:
        return "An example of using callbacks to dynamically modify a parameter's choices"

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def __init__(self, interface: xappt.BaseInterface, **kwargs):
        super().__init__(interface=interface, **kwargs)
        self.integer_choice.on_value_changed.add(self.on_integer_choice_changed)

    def on_integer_choice_changed(self, param: xappt.Parameter):
        item_key_string = param.choices[param.value]
        new_choices = ITEM_MAP[item_key_string]
        self.string_choice.choices = new_choices

    def execute(self, **kwargs) -> int:
        self.interface.message(f"You chose {self.string_choice.value}")
        return 0
