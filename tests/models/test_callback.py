import unittest

from xappt.models.callback import Callback


class CallbackFunction:
    def __init__(self):
        self.call_info = []

    def __call__(self, *args, **kwargs):
        self.call_info.append((args, kwargs))


class TestCallback(unittest.TestCase):
    def test_add(self):
        cb_fn = CallbackFunction()
        cb = Callback()
        cb.add(cb_fn)
        self.assertEqual(0, len(cb._callback_functions))
        cb._run_deferred_ops()
        self.assertEqual(1, len(cb._callback_functions))

    def test_add_auto_remove(self):
        cb_fn = CallbackFunction()
        cb = Callback()
        cb.add(cb_fn)
        cb._run_deferred_ops()
        self.assertEqual(1, len(cb._callback_functions))
        del cb_fn
        self.assertEqual(0, len(cb._callback_functions))

    def test_remove(self):
        cb_fn = CallbackFunction()
        cb = Callback()
        cb.add(cb_fn)
        cb._run_deferred_ops()
        self.assertEqual(1, len(cb._callback_functions))
        cb.remove(cb_fn)
        cb._run_deferred_ops()
        self.assertEqual(0, len(cb._callback_functions))
