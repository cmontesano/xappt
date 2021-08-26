import unittest

from xappt.utilities import humanize


class TestHumanize(unittest.TestCase):
    def test_humanize_list(self):
        test_cases = (
            ((1, 2, 3, 4, 5), "or", "1, 2, 3, 4, or 5"),
            (("a", "b", "c"), "except", "a, b, except c"),
            (("first", "second"), "and", "first and second"),
        )
        for values, conjunction, result in test_cases:
            with self.subTest(msg=f"values: {values}"):
                humanized = humanize.humanize_list(values, conjunction=conjunction)
                self.assertEqual(humanized, result)
