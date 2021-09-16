import os
import unittest

from typing import Any, Optional

from xappt.constants import TRUTHY_STRINGS
from xappt.models.parameter.errors import ParameterValidationError
from xappt.models.parameter.model import Parameter, ParameterDescriptor
from xappt.models.parameter.parameters import *
from xappt.models.parameter.validators import *
from xappt.models.plugins.interface import BaseInterface
from xappt.models.plugins.tool import BaseTool

from xappt.utilities.path.temp_path import temporary_path


class TestInterface(BaseInterface):
    def __init__(self):
        super().__init__()

    def run(self, **kwargs) -> int:
        return super().run(**kwargs)

    def invoke(self, plugin: BaseTool, **kwargs) -> int:
        pass

    def message(self, message: str):
        pass

    def warning(self, message: str):
        pass

    def error(self, message: str, *, details: Optional[str] = None):
        pass

    def ask(self, message: str) -> bool:
        pass

    def progress_start(self):
        pass

    def progress_update(self, message: str, percent_complete: float):
        pass

    def progress_end(self):
        pass


class TestValidators(unittest.TestCase):
    def test_base_validator(self):
        class PassthroughValidator(BaseValidator):
            def __init__(self, param: Parameter):
                super().__init__(param)
                self.call_log = {
                    'init': [param],
                    'validate': [],
                }

            def validate(self, value: Any) -> Any:
                self.call_log['validate'].append(value)
                return value

        class TestTool(BaseTool):
            int_param = ParamInt(validators=[PassthroughValidator])

            def execute(self, **kwargs) -> int:
                pass

        tt = TestTool(interface=TestInterface())
        self.assertIsInstance(tt.int_param.validators[-1], PassthroughValidator)
        call_log = tt.int_param.validators[-1].call_log
        self.assertEqual(1, len(call_log['validate']))
        tt.int_param.value = 5
        tt.validate()
        self.assertEqual(2, len(call_log['validate']))
        self.assertEqual(5, call_log['validate'][-1])

    def test_validate_required(self):
        class TestTool(BaseTool):
            test_param = ParameterDescriptor(data_type=int, required=True, validators=[ValidateRequired])

            def execute(self, **kwargs) -> int:
                pass

        tt = TestTool(interface=TestInterface())

        with self.assertRaises(ParameterValidationError):
            tt.test_param.validate(None)

        try:
            tt.test_param.validate(5)
        except ParameterValidationError:
            self.fail("Should not have thrown error")

    def test_validate_type_bool(self):
        class TestTool(BaseTool):
            test_param = ParameterDescriptor(data_type=bool, validators=[ValidateType])

            def execute(self, **kwargs) -> int:
                pass

        tt = TestTool(interface=TestInterface())
        for truthy_value in ("False", "0", 1, [5.5]):
            self.assertTrue(tt.test_param.validate(truthy_value))
        for falsy_value in (0, "", [], {}):
            self.assertFalse(tt.test_param.validate(falsy_value))

    def test_validate_type_int(self):
        class TestTool(BaseTool):
            test_param = ParameterDescriptor(data_type=int, validators=[ValidateType])

            def execute(self, **kwargs) -> int:
                pass

        tt = TestTool(interface=TestInterface())
        self.assertEqual(1, tt.test_param.validate("1"))
        self.assertEqual(235, tt.test_param.validate(235.1))

        with self.assertRaises(ParameterValidationError):
            tt.test_param.validate("invalid")

    def test_validate_default(self):
        class TestTool(BaseTool):
            test_param = ParameterDescriptor(data_type=int, default=42, validators=[ValidateDefault])
            test_param_no_default = ParameterDescriptor(data_type=int, validators=[ValidateDefault])

            def execute(self, **kwargs) -> int:
                pass

        tt = TestTool(interface=TestInterface())

        self.assertEqual(42, tt.test_param.value)
        self.assertEqual(42, tt.test_param.validate(None))
        self.assertEqual(27, tt.test_param.validate(27))

        # ValidateDefault doesn't care about type. It should just pass
        #   through anything if there is no default
        self.assertEqual("test", tt.test_param_no_default.validate("test"))

    def test_validate_default_int(self):
        class TestTool(BaseTool):
            test_param = ParameterDescriptor(data_type=int, default=42, validators=[ValidateDefaultInt])
            test_param_no_default = ParameterDescriptor(data_type=int, validators=[ValidateDefaultInt])
            test_param_choices = ParameterDescriptor(data_type=int, choices=("a", "b", "c"), default=1,
                                                     validators=[ValidateDefaultInt])
            test_param_choices_no_default = ParameterDescriptor(data_type=int, choices=("a", "b", "c"),
                                                                validators=[ValidateDefaultInt])

            def execute(self, **kwargs) -> int:
                pass

        tt = TestTool(interface=TestInterface())

        self.assertEqual(42, tt.test_param.value)
        self.assertEqual(0, tt.test_param_no_default.value)
        self.assertEqual("b", tt.test_param_choices.value)
        self.assertEqual("a", tt.test_param_choices_no_default.value)

    def test_validate_choice_int(self):
        class TestTool(BaseTool):
            test_param = ParameterDescriptor(data_type=int, choices=("a", "b", "c"), default=1,
                                             validators=[ValidateChoiceInt])
            test_param_no_default = ParameterDescriptor(data_type=int, choices=("a", "b", "c"),
                                                        validators=[ValidateChoiceInt])
            test_param_no_choices = ParameterDescriptor(data_type=int, validators=[ValidateChoiceInt])

            def execute(self, **kwargs) -> int:
                pass

        tt = TestTool(interface=TestInterface())

        with self.assertRaises(ParameterValidationError) as err:
            tt.test_param.validate("d")
        self.assertIn("must be one of", str(err.exception))

        try:
            tt.test_param.validate("a")
        except ParameterValidationError:
            self.fail()

        self.assertIsNone(tt.test_param_no_default.value)
        self.assertEqual(3, tt.test_param_no_choices.validate("3"))

        with self.assertRaises(ParameterValidationError):
            tt.test_param_no_choices.validate("invalid")

    def test_validate_choice_str(self):
        class TestTool(BaseTool):
            test_param = ParameterDescriptor(data_type=str, choices=("a", "b", "c"), default="b",
                                             validators=[ValidateChoiceStr])
            test_param_no_default = ParameterDescriptor(data_type=str, choices=("a", "b", "c"),
                                                        validators=[ValidateChoiceStr])
            test_param_no_choices = ParameterDescriptor(data_type=str, validators=[ValidateChoiceStr])

            def execute(self, **kwargs) -> int:
                pass

        tt = TestTool(interface=TestInterface())

        with self.assertRaises(ParameterValidationError):
            tt.test_param.validate("d")

        self.assertEqual("a", tt.test_param.validate("a"))

    def test_validate_range(self):
        class TestTool(BaseTool):
            test_param = ParameterDescriptor(data_type=int, validators=[ValidateDefault, (ValidateRange, 1, 10)],
                                             default=5)
            test_param_min = ParameterDescriptor(data_type=int, default=5,
                                                 validators=[ValidateDefault, (ValidateRange, 1, None)])
            test_param_max = ParameterDescriptor(data_type=int, default=5,
                                                 validators=[ValidateDefault, (ValidateRange, None, 10)])

            def execute(self, **kwargs) -> int:
                pass

        tt = TestTool(interface=TestInterface())

        with self.assertRaises(ParameterValidationError):
            tt.test_param.validate(11)

        try:
            tt.test_param.validate(3)
        except ParameterValidationError:
            self.fail()

        with self.assertRaises(ParameterValidationError):
            tt.test_param_min.validate(0)

        try:
            tt.test_param_max.validate(0)
        except ParameterValidationError:
            self.fail()

        with self.assertRaises(ParameterValidationError):
            tt.test_param_max.validate(11)

        try:
            tt.test_param_min.validate(11)
        except ParameterValidationError:
            self.fail()

    def test_validate_bool_from_string(self):
        v = ValidateBoolFromString(param=None)  # noqa

        for item in TRUTHY_STRINGS + ("0", "1", "3.5"):
            self.assertTrue(v.validate(item))

        for item in ("false", "False", "no", "invalid"):
            self.assertFalse(v.validate(item))

        for item in (0.0, 1, 2, 3.4, ['1', '2', '3'], {'abc': 123}):
            self.assertEqual(item, v.validate(item))

    def test_validate_choice_list(self):
        class TestTool(BaseTool):
            test_param = ParameterDescriptor(data_type=list, value=['a'], choices=("a", "b", "c"),
                                             validators=[ValidateChoiceList])
            test_param_no_choices = ParameterDescriptor(data_type=list, value=[], validators=[ValidateChoiceList])

            def execute(self, **kwargs) -> int:
                pass

        tt = TestTool(interface=TestInterface())

        with self.assertRaises(ParameterValidationError):
            tt.test_param.validate("d")

        self.assertEqual(55, tt.test_param_no_choices.validate(55))

    def test_validate_type_list(self):
        class TestTool(BaseTool):
            test_param = ParameterDescriptor(data_type=list, value=[], choices=("a", "b", "c"),
                                             validators=[ValidateTypeList])

            def execute(self, **kwargs) -> int:
                pass

        tt = TestTool(interface=TestInterface())

        self.assertListEqual(['1', '2', '3'], tt.test_param.validate("1;2;3"))

    def test_folder_exists(self):
        v = ValidateFolderExists(param=None)  # noqa

        with temporary_path() as tmp:
            folder = tmp.joinpath("folder")
            with self.assertRaises(ParameterValidationError):
                v.validate(str(folder))
            folder.mkdir()
            try:
                v.validate(str(folder))
            except ParameterValidationError:
                self.fail()
            last_path = os.getcwd()
            os.chdir(tmp)
            try:
                value = v.validate("folder")
            except ParameterValidationError:
                self.fail()
            else:
                self.assertEqual(str(folder), value)
            finally:
                os.chdir(last_path)

    def test_file_exists(self):
        v = ValidateFileExists(param=None)  # noqa

        with temporary_path() as tmp:
            file1 = tmp.joinpath("file1")
            with self.assertRaises(ParameterValidationError):
                v.validate(str(file1))
            file1.touch()
            last_path = os.getcwd()
            os.chdir(tmp)
            try:
                value = v.validate("file1")
            except ParameterValidationError:
                self.fail()
            else:
                self.assertEqual(str(file1), value)
            finally:
                os.chdir(last_path)
