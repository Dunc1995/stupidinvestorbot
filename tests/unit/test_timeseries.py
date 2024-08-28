import json
import unittest
from investorbot import timeseries


def get_example_data(filename: str) -> dict:
    example_data = None

    with open(f"./tests/unit/fixtures/{filename}", "r") as f:
        example_data = json.loads(f.read())["result"]["data"]

    return example_data


class TestTimeseries(unittest.TestCase):

    # Values determined via Google Sheets
    example_one_gradient = -0.000197
    example_one_gradient_decimals = 6
    example_one_offset = 4.53
    example_one_offset_decimals = 2

    example_two_gradient = 0.0908
    example_two_gradient_decimals = 4
    example_two_offset = 145
    example_two_offset_decimals = 0

    def setUp(self):
        pass

    def __test_get_line_of_best_fit(
        self,
        filename: str,
        t_grad: float,
        t_grad_dec: int,
        t_offset: float,
        t_offset_dec: int,
    ):
        data = get_example_data(filename)

        stats, _ = timeseries.get_time_series_data_frame(data)

        print(stats)

        a, b = timeseries.get_line_of_best_fit(stats)

        gradient = round(float(a), t_grad_dec)
        offset = round(float(b), t_offset_dec)

        self.assertAlmostEqual(
            gradient, t_grad, t_grad_dec, "Line of best fit gradient is incorrect"
        )
        self.assertAlmostEqual(
            offset, t_offset, t_offset_dec, "Line of best fit offset is incorrect"
        )

    def test_get_line_of_best_fit_one(self):
        """Testing I can replicate the trend line properties as calculated for the same dataset via
        Google Sheets."""
        self.__test_get_line_of_best_fit(
            "time-series-example-one.json",
            self.example_one_gradient,
            self.example_one_gradient_decimals,
            self.example_one_offset,
            self.example_one_offset_decimals,
        )

    def test_get_line_of_best_fit_two(self):
        """Testing I can replicate the trend line properties as calculated for the same dataset via
        Google Sheets."""
        self.__test_get_line_of_best_fit(
            "time-series-example-two.json",
            self.example_two_gradient,
            self.example_two_gradient_decimals,
            self.example_two_offset,
            self.example_two_offset_decimals,
        )


if __name__ == "__main__":
    unittest.main()
