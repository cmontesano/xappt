import importlib
import inspect
import os
import sys

from functools import partial
from itertools import chain
from typing import Generator, Optional, Tuple, Type

from xappt.constants import *
from xappt.config import log as logger
from xappt.models import BaseTool, BaseInterface
from xappt.models.plugins.base import BasePlugin

__all__ = [
    'get_tool_plugin',
    'get_interface_plugin',
    'get_interface',
    'register_plugin',
    'discover_plugins',
    'registered_tools',
    'registered_interfaces'
]


PLUGIN_REGISTRY = {
    PLUGIN_TYPE_TOOL: {},
    PLUGIN_TYPE_INTERFACE: {},
}


def get_tool_plugin(plugin_name: str) -> Type[BaseTool]:
    plugin = PLUGIN_REGISTRY[PLUGIN_TYPE_TOOL].get(plugin_name)
    if plugin is None:
        raise ValueError(f"Tool Plugin '{plugin_name}' not found")
    return plugin['class']


def get_interface_plugin(plugin_name: str) -> Type[BaseInterface]:
    plugin = PLUGIN_REGISTRY[PLUGIN_TYPE_INTERFACE].get(plugin_name)
    if plugin is None:
        raise ValueError(f"Interface Plugin '{plugin_name}' not found")
    return plugin['class']


def get_interface(interface_name: Optional[str] = None) -> BaseInterface:
    if interface_name is None:
        interface_class = get_interface_plugin(os.environ.get(INTERFACE_ENV, INTERFACE_DEFAULT))
    else:
        interface_class = get_interface_plugin(interface_name)
    return interface_class()


def _add_plugin_to_registry(plugin_class: Type[BasePlugin], *, visible: bool):
    if issubclass(plugin_class, BaseTool):
        plugin_type = PLUGIN_TYPE_TOOL
    elif issubclass(plugin_class, BaseInterface):
        plugin_type = PLUGIN_TYPE_INTERFACE
    else:
        raise NotImplementedError

    plugin_name = plugin_class.name()

    if plugin_name in PLUGIN_REGISTRY[plugin_type]:
        logger.warning(f"a plugin with the name '{plugin_name}' has already been registered")
        return False

    if not len(plugin_class.collection().strip()):
        logger.warning(f"Invalid collection '{plugin_class.collection()}' for plugin '{plugin_name}'")
        return False

    logger.debug(f"registered plugin '{plugin_name}'")
    PLUGIN_REGISTRY[plugin_type][plugin_name] = {
        "class": plugin_class,
        "visible": visible,
    }

    return True


def find_plugin_modules(path: str) -> Generator[str, None, None]:
    for item in os.scandir(path):  # type: os.DirEntry
        name_lower = item.name.lower()
        if not name_lower.startswith(PLUGIN_PREFIX):
            continue
        if name_lower.endswith((".dist-info", ".egg-info", ".egg-link")):
            continue
        yield item.name


def discover_plugins():
    logger.debug("discovering plugins")
    possible_plugin_modules = set()
    plugin_paths = set()

    env_paths = [path for path in os.environ.get(PLUGIN_PATH_ENV, "").split(os.pathsep) if len(path)]
    if len(env_paths):
        logger.debug(f"{PLUGIN_PATH_ENV}: {os.pathsep.join(env_paths)}")

    for p in chain(env_paths, sys.path):
        if len(p) == 0 or not os.path.isdir(p):
            continue
        logger.debug(f"scanning path for plugins: {p}")
        for module in find_plugin_modules(p):
            if module in possible_plugin_modules:
                continue
            logger.debug(f"found possible plugin module: {module}")
            possible_plugin_modules.add(module)
            plugin_paths.add(p)

    for p in plugin_paths:
        if p not in sys.path:
            logger.debug(f"adding to sys.path: {p}")
            sys.path.append(p)

    for module in possible_plugin_modules:
        logger.debug(f"importing module: {module}")
        try:
            importlib.import_module(module)
        except ImportError:
            logger.debug(f"could not import {module}", exc_info=True)
        logger.debug(f"importing module {module}.plugins")
        try:
            importlib.import_module(f"{module}.plugins")
        except ImportError:
            logger.debug(f"could not import {module}.plugins", exc_info=True)


def register_plugin(cls=None, *, active=True, visible=True):
    if cls is None:
        return partial(register_plugin, active=active, visible=visible)
    assert inspect.isclass(cls)
    if active:
        _add_plugin_to_registry(cls, visible=visible)
    else:
        logger.debug(f"skipping inactive plugin: {cls.__name__}")
    return cls


def registered_tools(*, include_hidden=False) -> Generator[Tuple[str, Type[BaseTool]], None, None]:
    for tool_name, tool_dict in PLUGIN_REGISTRY[PLUGIN_TYPE_TOOL].items():
        if not tool_dict['visible'] and not include_hidden:
            continue
        yield tool_name, tool_dict['class']


def registered_interfaces(*, include_hidden=False) -> Generator[Tuple[str, Type[BaseInterface]], None, None]:
    for iface_name, iface_dict in PLUGIN_REGISTRY[PLUGIN_TYPE_INTERFACE].items():
        if not iface_dict['visible'] and not include_hidden:
            continue
        yield iface_name, iface_dict['class']
