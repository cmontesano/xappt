import abc
import argparse

from typing import Optional

SubParser = type(argparse.ArgumentParser().add_subparsers())


class Plugin(metaclass=abc.ABCMeta):
    @classmethod
    def name(cls) -> Optional[str]:
        """ Return a custom string here to use as the display name of your plugin.
        This defaults to the lowercase version of your class name. """
        return cls.__name__.lower()

    @classmethod
    def help(cls) -> Optional[str]:
        """ Return some custom help text for your plugin. """
        return ""

    @classmethod
    def init_parser(cls, parent: SubParser):
        parser = parent.add_parser(cls.name().lower(), help=cls.help())
        cls.build_parser(parser)

    @classmethod
    @abc.abstractmethod
    def build_parser(cls, parent: argparse.ArgumentParser):
        pass

    @abc.abstractmethod
    def execute(self, **kwargs) -> int:
        pass
