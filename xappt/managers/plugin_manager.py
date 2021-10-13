import importlib
import inspect
import os
import pathlib
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

PLUGINS_DISCOVERED = False


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


def find_plugin_modules(path: pathlib.Path) -> Generator[pathlib.Path, None, None]:
    for item in path.iterdir():
        if not item.name.lower().startswith(PLUGIN_PREFIX):
            continue
        if item.suffix.lower() in (".dist-info", ".egg-info", ".egg-link"):
            continue
        yield item


def import_module(module_name: str, path: pathlib.Path) -> bool:
    path_str = str(path)
    old_sys_path = sys.path.copy()
    if path_str not in sys.path:
        sys.path.append(path_str)
    try:
        importlib.import_module(module_name)
    except ImportError:
        logger.debug(f"could not import '{module_name}'")
        sys.path = old_sys_path  # restore sys.path
    else:
        logger.debug(f"imported module '{module_name}'")
        return True
    return False


def discover_plugins(force: bool = False):
    global PLUGINS_DISCOVERED
    if PLUGINS_DISCOVERED and not force:
        logger.warning("Plugin discovery can only run once per session")
        return
    PLUGINS_DISCOVERED = True

    logger.debug("discovering plugins")
    imported_modules = set()

    env_paths = [path for path in os.environ.get(PLUGIN_PATH_ENV, "").split(os.pathsep) if len(path)]
    if len(env_paths):
        logger.debug(f"{PLUGIN_PATH_ENV}: {os.pathsep.join(env_paths)}")

    import copy
    sys_paths = copy.deepcopy(sys.path)
    checked_paths = []
    for p in chain(env_paths, sys_paths):
        if len(p) == 0 or not os.path.isdir(p):
            continue
        p = os.path.normpath(p)
        if p in checked_paths:
            logger.debug(f"path has already been scanned: '{p}'")
            continue
        checked_paths.append(p)
        logger.debug(f"scanning path for plugins at {p}")
        plugin_path = pathlib.Path(p)
        for module_path in find_plugin_modules(plugin_path):
            module_name = module_path.stem
            if module_name in imported_modules:
                logger.warning(f"conflicting module name '{module_name}' at {module_path}")
                continue
            logger.debug(f"attempting import of module '{module_name}'")
            if import_module(module_name, plugin_path) or import_module(f"{module_name}.plugins", plugin_path):
                imported_modules.add(module_name)


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
