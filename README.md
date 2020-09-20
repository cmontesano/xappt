# XAPPT - extensible application toolkit

![Python Unittest](https://github.com/cmontesano/xappt/workflows/Python%20Unittest/badge.svg)

**XAPPT** (pronounced like "zapped") is a toolkit that makes it easy to create  custom command line tools and invoke them from a uniform interface.

**XAPPT** requires Python 3.7 or higher.

To get started just create a subclass of `xappt.models.plugin.Plugin`, and make sure it's loadable by invoking your package, or a `plugins` submodule of your package. 

The name of your module should have the prefix "xappt". This allows automatic plugin discovery by scanning `sys.path`, and scanning paths defined on the environment variable `XAPPT_PLUGIN_PATH`.

### Getting started

If xappt is installed to the system Python interpreter, it should be available on the command line just by running the `xappt` command.

If everything is installed properly you should get output that looks like this:

```
$ xappt
usage: xappt [-h] [--version] {selfcheck} ...

positional arguments:
  {selfcheck}  Sub command help
    selfcheck  If running from a cloned copy of the git repository, check to
               see if the code being run matches the remote.

optional arguments:
  -h, --help   show this help message and exit
  --version    Display the version number
```

By default, only the `selfcheck` command is available. The `selfcheck` command is only really useful when working on **XAPPT** itself, or as an example.

So let's walk through creating a custom plugin. I'll be doing this on Linux, but the process is pretty similar on other systems.

First, make sure that xappt is installed:

    $ pip3 install xappt

Next, let's make sure that `xappt` is available on the command line:

```
$ xappt --version
xappt 0.0.3-4735e57
```

Now lets make a new plugin:

```
$ cd ~
$ mkdir -p temp/xappt_plugin
$ cd temp/xappt_plugin
$ touch __init__.py
```

We're created a folder named "temp", and inside of that a folder named "xappt_plugin". 

The reason for the two folders is so that we can add "temp" to `XAPPT_PLUGIN_PATH`, so that the "xappt_plugin" folder can be found inside of it. We'll get to that momentarily.

Then we create a new file in "xappt_plugin" named "\_\_init\_\_.py".

Now in `__init__.py` add the following code:

```python
import argparse

from xappt.models import Plugin
from xappt.managers.plugin_manager import register_plugin


@register_plugin
class MyPlugin(Plugin):
    @classmethod
    def help(cls) -> str:
        return "A simple command that will just echo the passed in arguments"

    @classmethod
    def build_parser(cls, parser: argparse.ArgumentParser):
        parser.add_argument("arg1", action="store", type=str)
        parser.add_argument("arg2", action="store", type=str)
        parser.add_argument("arg3", action="store", type=str)

    def execute(self, **kwargs) -> int:
        print(kwargs)
```

Finally, we have to add that "temp" folder to an environment variable to make our plugin discoverable, and then invoke xappt.

On Linux this would look something like this:

```
$ export XAPPT_PLUGIN_PATH=~/temp
$ xappt
```

On Windows it would look like this:

```
set XAPPT_PLUGIN_PATH=C:\path\to\temp
xappt
```

The output should now look like this:

```
usage: xappt [-h] [--version] {selfcheck,myplugin} ...

positional arguments:
  {selfcheck,myplugin}  Sub command help
    selfcheck           If running from a cloned copy of the git repository, check to 
                        see if the code being run matches the remote.
    myplugin            A simple command that will just echo the passed in arguments

optional arguments:
  -h, --help            show this help message and exit
  --version             Display the version number
```

And when running `xappt myplugin`:

```
$ xappt myplugin
usage: xappt myplugin [-h] arg1 arg2 arg3
xappt myplugin: error: the following arguments are required: arg1, arg2, arg3
```

So let's pass in some arguments:

```
$ xappt myplugin 1 2 3
{'version': False, 'command': 'myplugin', 'arg1': '1', 'arg2': '2', 'arg3': '3'}
```

For more complicated plugins you can have a structure like this:

```
/xappt_plugin
    /plugins
        __init__.py
        myplugin.py
    __init__.py
```

In this case `myplugin.py` would contain the `MyPlugin` class. And `xappt_plugin/plugins/__init__.py` might look like this:

```python
from .myplugin import MyPlugin
```

And that's it. Now feel free to make `execute` do something actually useful.
