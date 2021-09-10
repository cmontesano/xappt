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

    def test_weakref1(self):
        cb_fn = CallbackFunction()
        cb = Callback()
        cb.add(cb_fn)
        cb._run_deferred_ops()
        self.assertEqual(1, len(cb._callback_functions))
        cb.remove(cb_fn)
        cb._run_deferred_ops()
        self.assertEqual(0, len(cb._callback_functions))

    def test_weakref2(self):
        cb = Callback()
        cb.add(CallbackFunction())
        cb._run_deferred_ops()
        self.assertEqual(0, len(cb._callback_functions))

    def test_clear(self):
        cb_fn_1 = CallbackFunction()
        cb_fn_2 = CallbackFunction()
        cb_fn_3 = CallbackFunction()
        cb = Callback()
        cb.add(cb_fn_1)
        cb.add(cb_fn_2)
        cb.add(cb_fn_3)
        cb._run_deferred_ops()
        self.assertEqual(3, len(cb._callback_functions))
        cb.clear()
        cb._run_deferred_ops()
        self.assertEqual(0, len(cb._callback_functions))

    def test_invoke(self):
        cb_fn = CallbackFunction()
        cb = Callback()
        cb.add(cb_fn)
        cb.invoke("arg1", "arg2")
        self.assertEqual(1, len(cb_fn.call_info))
        self.assertIn("arg1", cb_fn.call_info[0][0])
        self.assertIn("arg2", cb_fn.call_info[0][0])

    def test_invoke_paused(self):
        cb_fn = CallbackFunction()
        cb = Callback()
        cb.add(cb_fn)
        self.assertFalse(cb.paused)
        cb.paused = True
        self.assertTrue(cb.paused)
        cb.invoke("arg1", "arg2")
        self.assertEqual(1, len(cb._callback_functions))
        self.assertEqual(0, len(cb_fn.call_info))
