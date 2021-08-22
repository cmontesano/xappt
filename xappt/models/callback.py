from collections import defaultdict
from typing import Callable, DefaultDict, Optional, Set

__all__ = ["Callback"]


class Callback:
    def __init__(self):
        self._callback_functions: Set[Callable] = set()
        self._deferred_operations: DefaultDict[str, Set[Optional[Callable]]] = defaultdict(set)
        self._paused = False

    def add(self, cb: Callable):
        self._deferred_operations['add'].add(cb)

    def remove(self, cb: Callable):
        self._deferred_operations['remove'].add(cb)

    def clear(self):
        self._deferred_operations['clear'].add(None)

    def _run_deferred_ops(self):
        for operation, functions in self._deferred_operations.items():
            op_fn = getattr(self._callback_functions, operation)
            for function in functions:
                if function is None:
                    op_fn()
                else:
                    try:
                        op_fn(function)
                    except KeyError:
                        pass
        self._deferred_operations.clear()

    def invoke(self, *args, **kwargs):
        self._run_deferred_ops()
        if self._paused:
            return
        for fn in self._callback_functions:
            fn(*args, **kwargs)

    @property
    def paused(self) -> bool:
        return self._paused

    @paused.setter
    def paused(self, value: bool):
        self._paused = value
