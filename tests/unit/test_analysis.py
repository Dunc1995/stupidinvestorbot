import json
import unittest
import uuid
from investorbot import analysis
from investorbot.enums import OrderStatus
from investorbot.models import BuyOrder
from investorbot.structs.internal import OrderDetail, PositionBalance


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

        stats, _ = analysis.get_time_series_data_frame(data)

        print(stats)

        a, b = analysis.get_line_of_best_fit(stats)

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

    def test_coin_sale_validator_is_ready_to_sell(self):
        """Covers basis for when all criteria has been met for the bot to sell a coin. It's now just
        a case of waiting for the coin value to reach an acceptable value."""
        buy_order = BuyOrder("123", "TON_USD", 6.6274)

        order_detail = OrderDetail(
            OrderStatus.COMPLETED.value,
            uuid.uuid4(),
            "TON_USD",
            4.970550,
            0.75,
            0.75,
            4.964925,
            0.00225,
            "TON",
            analysis.time_now() - 3_600_000,
        )
        position_balance = PositionBalance("TON", 4.88756072, 0.752975, 0.0)

        can_sell, _ = analysis.is_coin_sellable(
            buy_order, order_detail, position_balance
        )

        self.assertTrue(can_sell)

    def test_coin_sale_validator_will_not_sell_because_of_wallet_quantity(self):
        """A user may sell a coin manually, causing the original order quantity to be higher than
        what exists in the user's wallet. The bot needs to handle this gracefully."""
        buy_order = BuyOrder("123", "TON_USD", 6.6274)

        order_detail = OrderDetail(
            OrderStatus.COMPLETED.value,
            uuid.uuid4(),
            "TON_USD",
            4.970550,
            0.75,
            0.75,
            4.964925,
            0.00225,
            "TON",
            analysis.time_now() - 3_600_000,
        )
        position_balance = PositionBalance("TON", 0.056123, 0.01, 0.0)

        can_sell, validator = analysis.is_coin_sellable(
            buy_order, order_detail, position_balance
        )

        self.assertFalse(validator.order_has_not_been_filled)
        self.assertTrue(validator.wallet_balance_is_not_sufficient)
        self.assertFalse(can_sell)

    def test_coin_sale_validator_will_not_break_on_small_coin_balance(self):
        """A user may have a small amount of coin available whilst they have a pending buy order.
        This needs to be handled gracefully by the validator."""
        buy_order = BuyOrder("123", "TON_USD", 6.6274)

        order_detail = OrderDetail(
            OrderStatus.OTHER.value,
            uuid.uuid4(),
            "TON_USD",
            4.970550,
            0.75,
            0.00,
            0.00,
            0.00,
            "TON",
            analysis.time_now() - 3_600_000,
        )
        position_balance = PositionBalance("TON", 0.056123, 0.01, 0.0)

        can_sell, validator = analysis.is_coin_sellable(
            buy_order, order_detail, position_balance
        )

        self.assertTrue(validator.order_has_not_been_filled)
        self.assertFalse(validator.wallet_balance_is_not_sufficient)
        self.assertFalse(can_sell)

    def test_coin_sale_validator_will_not_break_on_normal_coin_balance(self):
        """A user may have an amount of coin available whilst they have a pending buy order. This
        needs to be handled gracefully by the validator."""
        buy_order = BuyOrder("123", "TON_USD", 6.6274)

        order_detail = OrderDetail(
            OrderStatus.OTHER.value,
            uuid.uuid4(),
            "TON_USD",
            4.970550,
            0.75,
            0.00,
            0.00,
            0.00,
            "TON",
            analysis.time_now() - 3_600_000,
        )
        position_balance = PositionBalance("TON", 5.3, 0.8, 0.0)

        can_sell, validator = analysis.is_coin_sellable(
            buy_order, order_detail, position_balance
        )

        self.assertTrue(validator.order_has_not_been_filled)
        self.assertFalse(validator.wallet_balance_is_not_sufficient)
        self.assertFalse(validator.no_coin_balance)
        self.assertFalse(validator.order_has_been_cancelled)
        self.assertFalse(validator.order_balance_has_already_been_sold)
        self.assertFalse(can_sell)
