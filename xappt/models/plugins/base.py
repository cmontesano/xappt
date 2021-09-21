from xappt.models.mixins import ConfigMixin
from xappt.utilities.path import user_data_path


class BasePlugin(ConfigMixin):
    def __init__(self):
        super().__init__()
        self._data_dict = {}
        config_file = f"{self.collection()}-{self.name()}.cfg"
        self.config_path = user_data_path().joinpath("xappt").joinpath("plugins").joinpath(config_file)
        self.init_config()

    def init_config(self):
        pass

    @classmethod
    def name(cls) -> str:
        """ Use this to specify the name of your plugin. """
        return cls.__name__.lower()

    @classmethod
    def help(cls) -> str:
        """ Provide a short help string or description. """
        return ""

    @classmethod
    def collection(cls) -> str:
        """ Use this to group your plugin with other like plugins. """
        return ""
