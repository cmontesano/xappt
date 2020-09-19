import argparse
import sys

from xappt.__version__ import __version__, __build__
from xappt.managers import plugin_manager


def main(*argv) -> int:
    plugin_manager.discover_plugins()

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true', dest='version', help='Display the version number')
    subparsers = parser.add_subparsers(help="Sub command help", dest='command')

    for plugin_name, plugin_dict in plugin_manager.PLUGIN_REGISTRY.items():
        plugin_dict['class'].init_parser(subparsers)

    options = parser.parse_args(args=argv)

    if options.version:
        print(f"xappt {__version__}-{__build__}")
        return 0

    if options.command in plugin_manager.PLUGIN_REGISTRY:
        plugin = plugin_manager.PLUGIN_REGISTRY[options.command]['class']()
        return plugin.execute(**options.__dict__)

    parser.print_help()

    return 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
