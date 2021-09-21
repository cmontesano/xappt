import unittest

from xappt.models.parameter.meta import ParamMeta
from xappt.models.parameter.model import Parameter
from xappt.models.parameter.parameters import *


class TestParamMeta(unittest.TestCase):
    def test_metaclass_no_bases(self):
        class TestMeta(metaclass=ParamMeta):
            pass

        tm = TestMeta()
        self.assertListEqual([], tm._parameters_)

    def test_metaclass_multiple_bases(self):
        class TestMetaA(metaclass=ParamMeta):
            param1 = ParamString()

        class TestMetaB(metaclass=ParamMeta):
            param2 = ParamInt()

        class TestMetaAB(TestMetaA, TestMetaB, metaclass=ParamMeta):
            pass

        tm = TestMetaAB()
        self.assertListEqual(['param1', 'param2'], tm._parameters_)
        self.assertIsInstance(tm.param1, Parameter)
        self.assertIsInstance(tm.param2, Parameter)

    def test_metaclass_subclass_override(self):
        class TestMetaA(metaclass=ParamMeta):
            param1 = ParamString()

        class TestMetaB(TestMetaA, metaclass=ParamMeta):
            param1 = ParamInt()

        tm = TestMetaB()
        self.assertListEqual(['param1'], tm._parameters_)
        self.assertIsInstance(tm.param1, Parameter)
        self.assertIs(tm.param1.data_type, int)
