class BasePlugin:
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
