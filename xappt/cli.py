import argparse
import sys

import xappt

from xappt.models.parameter import convert


def cli_main(*argv) -> int:
    xappt.plugin_manager.discover_plugins()

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true', dest='version', help='Display the version number')
    subparsers = parser.add_subparsers(help="Sub command help", dest='command')

    for plugin_name, plugin_dict in xappt.plugin_manager.PLUGIN_REGISTRY.items():
        cls = plugin_dict['class']
        plugin_parser = subparsers.add_parser(cls.name().lower(), help=cls.help())
        for param_name in cls._parameters_:
            parameter = getattr(cls, param_name)
            setup_args = parameter.param_setup_args
            args, kwargs = convert.to_argument_dict(setup_args)
            plugin_parser.add_argument(*args, **kwargs)

    options = parser.parse_args(args=argv)

    if options.version:
        print(f"xappt {xappt.version_str}")
        return 0

    if options.command in xappt.plugin_manager.PLUGIN_REGISTRY:
        plugin_class = xappt.plugin_manager.PLUGIN_REGISTRY[options.command]['class']
        plugin_instance = plugin_class(**options.__dict__)
        return plugin_instance.execute()

    parser.print_help()

    return 0


def entry_point() -> int:
    return cli_main(*sys.argv[1:])


if __name__ == '__main__':
    print(xappt.version)
    sys.exit(entry_point())
