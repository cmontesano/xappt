import argparse
import sys

from typing import Dict, List, Tuple

from xappt.__version__ import __version__, __build__
from xappt.managers import plugin_manager


def parameter_to_argument_dict(parameter_dict: Dict) -> Tuple[List, Dict]:
    positional_args = [f"--{parameter_dict['name']}"]
    if parameter_dict['short_name'] is not None:
        positional_args.append(f"-{parameter_dict['short_name']}")

    keyword_args = {}
    if parameter_dict['data_type'] == bool:
        keyword_args['action'] = 'store_true'
    else:
        keyword_args['action'] = 'store'
        keyword_args['type'] = parameter_dict['data_type']

    keyword_args['help'] = parameter_dict['description']

    if not parameter_dict['required']:
        keyword_args['default'] = parameter_dict['default']
    else:
        keyword_args['required'] = True

    return positional_args, keyword_args


def main(*argv) -> int:
    plugin_manager.discover_plugins()

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true', dest='version', help='Display the version number')
    subparsers = parser.add_subparsers(help="Sub command help", dest='command')

    for plugin_name, plugin_dict in plugin_manager.PLUGIN_REGISTRY.items():
        cls = plugin_dict['class']
        plugin_parser = subparsers.add_parser(cls.name().lower(), help=cls.help())
        for param_name in cls._parameters_:
            parameter = getattr(cls, param_name)
            setup_args = parameter.param_setup_args
            args, kwargs = parameter_to_argument_dict(setup_args)
            plugin_parser.add_argument(*args, **kwargs)

    options = parser.parse_args(args=argv)

    if options.version:
        print(f"xappt {__version__}-{__build__}")
        return 0

    if options.command in plugin_manager.PLUGIN_REGISTRY:
        plugin_class = plugin_manager.PLUGIN_REGISTRY[options.command]['class']
        plugin_instance = plugin_class(**options.__dict__)
        return plugin_instance.execute()

    parser.print_help()

    return 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
