import unittest

from xappt.models.callback import Callback


class CallbackHost:
    def __init__(self):
        self.call_info = {
            'a': [],
            'b': [],
            'c': [],
        }

    def callback_method_a(self, *args, **kwargs):
        self.call_info['a'].append((args, kwargs))

    def callback_method_b(self, *args, **kwargs):
        self.call_info['b'].append((args, kwargs))

    def callback_method_c(self, *args, **kwargs):
        self.call_info['c'].append((args, kwargs))


class TestCallback(unittest.TestCase):
    def test_add(self):
        cb_host = CallbackHost()
        cb = Callback()
        cb.add(cb_host.callback_method_a)
        self.assertEqual(0, len(cb._callback_functions))
        cb._run_deferred_ops()
        self.assertEqual(1, len(cb._callback_functions))

    def test_add_auto_remove(self):
        cb_host = CallbackHost()
        cb = Callback()
        cb.add(cb_host.callback_method_a)
        cb._run_deferred_ops()
        self.assertEqual(1, len(cb._callback_functions))
        del cb_host
        cb._run_deferred_ops()
        self.assertEqual(0, len(cb._callback_functions))

    def test_weakref(self):
        cb_host = CallbackHost()
        cb = Callback()
        cb.add(cb_host.callback_method_a)
        cb._run_deferred_ops()
        self.assertEqual(1, len(cb._callback_functions))
        cb.remove(cb_host.callback_method_a)
        cb._run_deferred_ops()
        self.assertEqual(0, len(cb._callback_functions))

    def test_clear(self):
        cb_host = CallbackHost()
        cb = Callback()
        cb.add(cb_host.callback_method_a)
        cb.add(cb_host.callback_method_b)
        cb.add(cb_host.callback_method_c)
        cb._run_deferred_ops()
        self.assertEqual(3, len(cb._callback_functions))
        cb.clear()
        cb._run_deferred_ops()
        self.assertEqual(0, len(cb._callback_functions))

    def test_invoke(self):
        cb_host = CallbackHost()
        cb = Callback()
        cb.add(cb_host.callback_method_a)
        cb.invoke("arg1", "arg2")
        call_info = cb_host.call_info['a']
        self.assertEqual(1, len(call_info))
        self.assertIn("arg1", call_info[0][0])
        self.assertIn("arg2", call_info[0][0])

    def test_invoke_paused(self):
        cb_host = CallbackHost()
        cb = Callback()
        cb.add(cb_host.callback_method_a)
        self.assertFalse(cb.paused)
        cb.paused = True
        self.assertTrue(cb.paused)
        cb.invoke("arg1", "arg2")
        self.assertEqual(1, len(cb._callback_functions))
        self.assertEqual(0, len(cb_host.call_info['a']))
