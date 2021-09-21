import shutil
import textwrap

from math import floor
from typing import Callable, Dict, Optional, Type

import colorama
from colorama import Fore, Back

import xappt

from xappt.models.parameter.model import Parameter


# noinspection PyMethodMayBeStatic
@xappt.register_plugin
class StdIO(xappt.BaseInterface):
    def __init__(self):
        super().__init__()

        self.prompt_dispatch: Dict[Type, Callable] = {
            int: self.prompt_int,
            bool: self.prompt_bool,
            str: self.prompt_str,
            list: self.prompt_list,
        }

        self._progress_started = None
        self._term_size = (80, 25)

        colorama.init(autoreset=True)

        self.on_write_stdout.add(self.write_stdout_callback)
        self.on_write_stderr.add(self.write_stderr_callback)

    def message(self, message: str):
        self._clear_progress()
        print(message)

    def warning(self, message: str):
        self._clear_progress()
        print(f"{Fore.YELLOW}WARNING: {message}")

    def error(self, message: str, *, details: Optional[str] = None):
        self._clear_progress()
        print(f"{Fore.RED}ERROR: {message}")
        if details is not None and len(details):
            print(f"{Fore.RED}{textwrap.indent(details, '    ')}")

    def ask(self, message: str) -> bool:
        self._clear_progress()
        choices = ("y", "n")
        while True:
            result = input(f"{message} ({'|'.join(choices)}) ")
            if result not in choices:
                print(f"Please enter {xappt.humanize_list(choices)}")
                continue
            break
        return choices.index(result) == 0

    def progress_start(self):
        if self._progress_started:
            self.progress_end()
        self._progress_started = True
        self._term_size = shutil.get_terminal_size()

    def progress_update(self, message: str, percent_complete: float):
        if not self._progress_started:
            raise RuntimeError("`progress_start` not called.")

        percent_complete = max(0.0, min(1.0, percent_complete))

        max_width = self._term_size[0]
        message = textwrap.shorten(message, width=max_width).ljust(max_width)

        progress_width = int(floor(max_width * percent_complete))
        message_head = message[:progress_width]
        message_tail = message[progress_width:]

        print(f"\r{Fore.BLACK}{Back.WHITE}{message_head}{Fore.RESET}{Back.RESET}{message_tail}", end="")

    def progress_end(self):
        if not self._progress_started:
            return
        print("")
        self._progress_started = False

    def _clear_progress(self):
        """ Clear progress bar to allow more graceful interruptions. """
        if not self._progress_started:
            return
        clear_line = " " * self._term_size[0]
        print(f"\r{clear_line}\r", end="")

    def invoke(self, plugin: xappt.BaseTool, **kwargs):
        try:
            for param in plugin.parameters():
                if not param.hidden:
                    self.prompt_for_param(param)
                else:
                    param.value = param.validate(param.default)
            return plugin.execute(**kwargs)
        except KeyboardInterrupt:
            print("")
            self.error("Aborted by user")
            return 1

    # noinspection PyMethodMayBeStatic
    def prompt_default(self, param: Parameter) -> str:
        if param.default is not None:
            return f"{param.name} ({param.default}): "
        return f"{param.name}: "

    def prompt_int(self, param: Parameter) -> str:
        if param.choices is not None:
            if param.default is not None:
                choice_values = []
                for i, value in enumerate(param.choices):
                    if i == param.default:
                        choice_values.append(f'{value}*')
                    else:
                        choice_values.append(value)
            else:
                choice_values = param.choices
            return f"{param.name} ({'|'.join(choice_values)}): "
        return self.prompt_default(param)

    def prompt_str(self, param: Parameter) -> str:
        if param.choices is not None:
            choice_values = []
            for value in param.choices:
                if value == param.default:
                    choice_values.append(f'{value}*')
                else:
                    choice_values.append(value)
            return f"{param.name} ({'|'.join(choice_values)}): "
        return self.prompt_default(param)

    # noinspection PyMethodMayBeStatic
    def prompt_bool(self, param: Parameter) -> str:
        choices = "(y|n)"
        if param.default is not None:
            if param.default:
                choices = "(y*|n)"
            else:
                choices = "(y|n*)"
        return f"{param.name} {choices}: "

    def prompt_list(self, param: Parameter) -> str:
        choice_values = []
        try:
            iter(param.default)
        except TypeError:
            default_values = [param.default]
        else:
            if isinstance(param.default, str):
                # a string is iterable, but we want to treat it as a single value
                default_values = [param.default]
            else:
                default_values = param.default
        for value in param.choices:
            if value in default_values:
                choice_values.append(f'{value}*')
            else:
                choice_values.append(value)
        return f"{param.name} ({'|'.join(choice_values)}): "

    def prompt_for_param(self, param: Parameter):
        prompt_fn = self.prompt_dispatch.get(param.data_type, self.prompt_default)
        prompt = prompt_fn(param)

        print("")
        if len(param.description):
            print(param.description)

        while True:
            value = input(prompt)
            if len(value) == 0:
                value = None
            try:
                param.value = param.validate(value)
            except BaseException as e:
                print(f"{Fore.RED}Error: {e}")
                print("Try again")
                print("")
            else:
                break

    def run(self, **kwargs) -> int:
        return super().run(**kwargs)

    def write_stdout_callback(self, text: str):
        print(text)

    def write_stderr_callback(self, text: str):
        print(f"{Fore.RED}{text}")


def test_progress():
    import time
    time.sleep(1.0)

    interface = StdIO()
    interface.progress_start()
    for i in range(1000):
        interface.progress_update("test progress", i / 1000)
        time.sleep(0.005)
        if i == 250:
            interface.message("interrupting message")
        if i == 500:
            interface.warning("interrupting warning")
        if i == 750:
            interface.error("interrupting error", details="Error details\nthat possibly span\nmultiple lines")
    interface.progress_update("done", 1.0)
    interface.progress_end()
    interface.message("complete")


if __name__ == '__main__':
    test_progress()
