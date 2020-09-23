import abc

from xappt.models.plugins.base import BasePlugin
from xappt.models.plugins.tool import BaseTool


class BaseInterface(BasePlugin, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def invoke(self, plugin: BaseTool, **kwargs):
        pass
