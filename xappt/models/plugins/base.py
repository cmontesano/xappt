class BasePlugin:
    @classmethod
    def name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def help(cls) -> str:
        return ""
