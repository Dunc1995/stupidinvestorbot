from dataclasses import dataclass
from investorbot.decorators import no_scientific_notation


@dataclass
class ScientificNotationTestObject:
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


def test_numerical_values_print_correctly():
    """There are many different edge cases for converting numerical types to strings. I want to
    ensure here that my no_scientific_notation converts any numerical value to a string that
    looks like the float as it is written - i.e. no floating point precision weirdness, or
    scientific notation. This is only really a problem when interacting with the Crypto API.
    """

    obj = ScientificNotationTestObject()

    assert obj.small_float_one == "0.0000008"
    assert obj.small_float_two == "0.000343115"
    assert obj.small_float_three == "0.000000031343431"
    assert obj.normal_float == "10.4987"
    assert obj.large_float_one == "80000000000000.0"
    assert obj.large_float_two == "13440900000000.0"
    assert obj.small_integer == "1"
    assert obj.large_integer == "80000000000000"
