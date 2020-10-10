#!/usr/bin/env python3

import argparse
import os
import sys

from collections import defaultdict
from itertools import chain
from typing import DefaultDict, List

import colorama
from colorama import Fore

import xappt

from xappt.models.parameter import convert


def build_parser() -> argparse.ArgumentParser:
    interface_list = [i[0] for i in xappt.plugin_manager.registered_interfaces()]
    default_interface_name = os.environ.get(xappt.INTERFACE_ENV, xappt.INTERFACE_DEFAULT)

    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--version', action='store_true',
                        help='Display the version number and build')
    parser.add_argument('-l', '--list', action='store_true',
                        help='List all of the discovered plugins')
    parser.add_argument('-i', '--interface', choices=interface_list, default=default_interface_name,
                        help='Specify the name of the default user interface. '
                             f'This can also be done by setting the environment variable {xappt.INTERFACE_ENV}')
    parser.add_argument('--ui', action='store_true', dest="interactive",
                        help='Run the specified tool interactively using the passed command line arguments, '
                             'otherwise it will be invoked with the default interface.')

    subparsers = parser.add_subparsers(help="Sub command help", dest='command')

    for plugin_name, plugin_class in xappt.plugin_manager.registered_tools():
        plugin_parser = subparsers.add_parser(plugin_class.name(), help=plugin_class.help())
        for parameter in plugin_class.class_parameters():
            setup_args = parameter.param_setup_args
            args, kwargs = convert.to_argument_dict(setup_args)
            plugin_parser.add_argument(*args, **kwargs)

    return parser


def list_all_plugins():
    colorama.init(autoreset=True)

    plugin_list: DefaultDict[str, List[str]] = defaultdict(list)

    for _, plugin_class in chain(xappt.plugin_manager.registered_interfaces(), xappt.plugin_manager.registered_tools()):
        collection = plugin_class.collection()
        plugin_list[collection].append(f"{Fore.LIGHTBLUE_EX}{plugin_class.name()} "
                                       f"{Fore.WHITE}({plugin_class.help() or 'No help text'})")

    for collection in sorted(plugin_list.keys()):
        print(f"{Fore.GREEN}{collection}")
        for plugin in sorted(plugin_list[collection]):
            print(f"    {plugin}")


def cli_main(*argv) -> int:
    parser = build_parser()
    options = parser.parse_args(args=argv)

    if options.version:
        print(f"xappt {xappt.version_str}")
        return 0

    if options.list:
        list_all_plugins()
        return 0

    os.environ[xappt.INTERFACE_ENV] = options.interface

    if options.command is not None:
        plugin_class = xappt.plugin_manager.get_tool_plugin(options.command)
        plugin_instance = plugin_class(**options.__dict__)
        if options.interactive:
            interface = xappt.plugin_manager.get_interface()
            interface.invoke(plugin_instance)
        else:
            plugin_instance.validate()
            interface = xappt.plugin_manager.get_interface("stdio")
            return plugin_instance.execute(interface=interface)
    else:
        parser.print_help()

    return 0


def entry_point() -> int:
    xappt.discover_plugins()
    return cli_main(*sys.argv[1:])


if __name__ == '__main__':
    sys.exit(entry_point())
