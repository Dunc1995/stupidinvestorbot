import unittest

from investorbot.decorators import no_scientific_notation


class TestDecorators(unittest.TestCase):
    def setUp(self):
        pass

    @property
    @no_scientific_notation
    def small_float_one(self) -> float:
        return 0.0000008

    @property
    @no_scientific_notation
    def small_float_two(self) -> float:
        return 0.000343115

    @property
    @no_scientific_notation
    def small_float_three(self) -> float:
        return 0.000000031343431

    @property
    @no_scientific_notation
    def normal_float(self) -> float:
        return 10.4987

    @property
    @no_scientific_notation
    def large_float_one(self) -> float:
        return 80000000000000.0

    @property
    @no_scientific_notation
    def large_float_two(self) -> float:
        return 13440900000000.0

    @property
    @no_scientific_notation
    def small_integer(self) -> int:
        return 1

    @property
    @no_scientific_notation
    def large_integer(self) -> int:
        return 80000000000000

    def test_numerical_values_print_correctly(self):
        self.assertEqual(self.small_float_one, "0.0000008")
        self.assertEqual(self.small_float_two, "0.000343115")
        self.assertEqual(self.small_float_three, "0.000000031343431")
        self.assertEqual(self.normal_float, "10.4987")
        self.assertEqual(self.large_float_one, "80000000000000.0")
        self.assertEqual(self.large_float_two, "13440900000000.0")
        self.assertEqual(self.small_integer, "1")
        self.assertEqual(self.large_integer, "80000000000000")


if __name__ == "__main__":
    unittest.main()
