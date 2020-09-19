import importlib
import inspect
import logging
import os
import re
import sys

from functools import partial

__all__ = ['get_plugin', 'register_plugin', 'discover_plugins']

logger = logging.getLogger("xappt")

PLUGIN_REGISTRY = {}
PLUGIN_NAME_PATTERN = re.compile(r"(?P<group>\S+)\.(?P<section>\S+)\.(?P<name>\S+)")


def registered_plugins():
    PLUGIN_REGISTRY.keys()


def get_plugin(plugin_name):
    plugin = PLUGIN_REGISTRY.get(plugin_name)
    if plugin is None:
        raise ValueError("Plugin '{}' not found".format(plugin_name))
    return plugin['class']


def validate_plugin_name(name):
    match = PLUGIN_NAME_PATTERN.match(name)
    if match is None:
        raise ValueError("Invalid plugin name: '{}'".format(name))


def _add_plugin_to_registry(plugin_class):
    from xappt.models import Plugin

    assert issubclass(plugin_class, Plugin)

    plugin_name = plugin_class.name()

    if plugin_name in PLUGIN_REGISTRY:
        logger.warning(f"a plugin with the name {plugin_name} has already been registered")
        return False

    logger.debug(f"registered plugin '{plugin_name}'")
    PLUGIN_REGISTRY[plugin_name] = {"class": plugin_class}

    return True


def discover_plugins():
    possible_plugin_modules = {"xappt"}

    for p in sys.path:
        if len(p) == 0 or not os.path.isdir(p):
            continue
        for item in os.scandir(p):
            name_lower = item.name.lower()
            if not name_lower.startswith('xappt'):
                continue
            if name_lower.count(".dist-info") or name_lower.count(".egg-info"):
                continue
            logger.debug("discovered {}".format(item.path))
            possible_plugin_modules.add(item.name)
    for module in sorted(list(possible_plugin_modules)):
        logger.debug("importing module {}".format(module))
        try:
            importlib.import_module(module)
        except ImportError:
            logger.warning(f"could not import {module}", exc_info=True)
        logger.debug(f"importing module {module}.plugins")
        try:
            importlib.import_module(f"{module}.plugins")
        except ImportError:
            logger.warning(f"could not import {module}.plugins", exc_info=True)


def register_plugin(cls=None, *, active=True):
    if cls is None:
        return partial(register_plugin, active=active)
    assert inspect.isclass(cls)
    if active:
        _add_plugin_to_registry(cls)
    else:
        logger.debug(f"skipping inactive plugin: {cls.__name__}")
    return cls
