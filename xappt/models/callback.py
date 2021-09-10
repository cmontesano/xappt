from weakref import WeakSet

from collections import defaultdict
from typing import Callable, DefaultDict, Optional, Set

__all__ = ["Callback"]


class Callback:
    """ A simple object to run callback functions. Note that adding, removing,
    or clearing the set of functions is deferred until the next time `invoke` is
    called. This ensures that we're not modifying the callback set while we're
    iterating through it.
    """

    def __init__(self):
        self._callback_functions: WeakSet[Callable] = WeakSet()
        self._deferred_operations: DefaultDict[str, Set[Optional[Callable]]] = defaultdict(set)
        self._paused = False

    def add(self, cb: Callable):
        self._deferred_operations['add'].add(cb)

    def remove(self, cb: Callable):
        self._deferred_operations['remove'].add(cb)

    def clear(self):
        self._deferred_operations['clear'].add(None)

    def _run_deferred_ops(self):
        """ Process any queued operations for `self._callback_functions`. The
        methods `add`, `remove`, and `clear` build the `self._deferred_operations`
        dictionary which has the following format:

        {
            'add': {callable1, callable2},
            'remove': {callable3, callable4},
            'clear': {None},
        }

        When iterating through this dictionary we look up the key as an
        attribute of the `self._callback_functions` WeakSet, and then pass
        each callable as an argument to that function. With the above
        dictionary this is equivalent to:

        self._callback_functions.add(callable1)
        self._callback_functions.add(callable2)
        self._callback_functions.remove(callable3)
        self._callback_functions.remove(callable4)
        self._callback_functions.clear()

        """
        for op_name, callables in self._deferred_operations.items():
            op_method = getattr(self._callback_functions, op_name)
            for fn in callables:
                if fn is None:
                    op_method()
                else:
                    try:
                        op_method(fn)
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
