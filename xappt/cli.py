import argparse
import sys

import xappt

from xappt.models.parameter import convert


def cli_main(*argv) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true', dest='version', help='Display the version number')
    subparsers = parser.add_subparsers(help="Sub command help", dest='command')

    for plugin_name, plugin_class in xappt.plugin_manager.registered_tools():
        assert issubclass(plugin_class, xappt.BaseTool)
        plugin_parser = subparsers.add_parser(plugin_class.name().lower(), help=plugin_class.help())
        for parameter in plugin_class.class_parameters():
            setup_args = parameter.param_setup_args
            args, kwargs = convert.to_argument_dict(setup_args)
            plugin_parser.add_argument(*args, **kwargs)

    options = parser.parse_args(args=argv)

    if options.version:
        print(f"xappt {xappt.version_str}")
        return 0

    if options.command is not None:
        try:
            plugin_class = xappt.plugin_manager.get_tool_plugin(options.command)
        except ValueError:
            print(f"Plugin {options.command} not found")
        else:
            plugin_instance = plugin_class(**options.__dict__)
            return plugin_instance.execute()

    parser.print_help()

    return 0


def entry_point() -> int:
    xappt.discover_plugins()
    return cli_main(*sys.argv[1:])


if __name__ == '__main__':
    sys.exit(entry_point())
