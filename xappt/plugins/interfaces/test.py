from collections import defaultdict
from typing import Optional

import xappt


class TestInterface(xappt.BaseInterface):
    def __init__(self):
        super().__init__()
        self.ask_result: bool = True
        self.messages = defaultdict(list)

    def run(self, **kwargs) -> int:
        return super().run(**kwargs)

    def invoke(self, plugin: xappt.BaseTool, **kwargs) -> int:
        return plugin.execute(**kwargs)

    def message(self, message: str):
        self.messages['message'].append(message)

    def warning(self, message: str):
        self.messages['warning'].append(message)

    def error(self, message: str, *, details: Optional[str] = None):
        self.messages['error'].append((message, details))

    def ask(self, message: str) -> bool:
        return self.ask_result

    def progress_start(self):
        pass

    def progress_update(self, message: str, percent_complete: float):
        pass

    def progress_end(self):
        pass
