from __future__ import annotations

import weakref

from collections import defaultdict
from typing import Callable, Optional

__all__ = ["Callback"]


class Callback:
    """ A simple object to run callback functions. Note that adding, removing,
    or clearing the set of functions is deferred until the next time `invoke` is
    called. This ensures that we're not modifying the callback set while we're
    iterating through it.
    """

    def __init__(self):
        self._callback_functions: set[Callable] = set()
        self._deferred_operations: defaultdict[str, set[Optional[Callable]]] = defaultdict(set)
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
        attribute of the `self._callback_functions` set, and then pass
        each callable as an argument to that function. With the above
        dictionary this is equivalent to:

        self._callback_functions.add(callable1)
        self._callback_functions.add(callable2)
        self._callback_functions.remove(callable3)
        self._callback_functions.remove(callable4)
        self._callback_functions.clear()

        """
        while self._deferred_operations:
            op_name, callables = self._deferred_operations.popitem()
            op_method = getattr(self._callback_functions, op_name)
            for fn in callables:
                if fn is None:
                    op_method()
                else:
                    try:
                        ref = weakref.WeakMethod(fn)
                    except TypeError:
                        op_method(weakref.ref(fn))
                    else:
                        op_method(ref)
        self._clear_dead_refs()

    def _clear_dead_refs(self):
        refs_to_remove = set()
        for fn in self._callback_functions:
            if fn() is None:
                refs_to_remove.add(fn)
        for fn in refs_to_remove:
            self._callback_functions.remove(fn)

    def invoke(self, *args, **kwargs):
        self._run_deferred_ops()
        if self._paused:
            return
        for fn in self._callback_functions:
            fn()(*args, **kwargs)

    @property
    def paused(self) -> bool:
        return self._paused

    @paused.setter
    def paused(self, value: bool):
        self._paused = value
