import json
import unittest
import uuid

from investorbot import timeseries
from investorbot.enums import OrderStatus
from investorbot.models import BuyOrder
from investorbot.structs.internal import OrderDetail, PositionBalance
from investorbot.validators import is_coin_sellable


class TestValidators(unittest.TestCase):
    def setUp(self):
        pass

    def test_coin_sale_validator_is_ready_to_sell(self):
        """Covers basis for when all criteria has been met for the bot to sell a coin. It's now just
        a case of waiting for the coin value to reach an acceptable value."""
        buy_order = BuyOrder("123", "TON_USD", 6.6274)

        order_detail = OrderDetail(
            OrderStatus.FILLED.value,
            uuid.uuid4(),
            "TON_USD",
            4.970550,
            0.75,
            0.75,
            4.964925,
            0.00225,
            "TON",
            timeseries.time_now() - 3_600_000,
        )
        position_balance = PositionBalance("TON", 4.88756072, 0.752975, 0.0)

        can_sell, _ = is_coin_sellable(buy_order, order_detail, position_balance)

        self.assertTrue(can_sell)

    def test_coin_sale_validator_will_not_sell_because_of_wallet_quantity(self):
        """A user may sell a coin manually, causing the original order quantity to be higher than
        what exists in the user's wallet. The bot needs to handle this gracefully."""
        buy_order = BuyOrder("123", "TON_USD", 6.6274)

        order_detail = OrderDetail(
            OrderStatus.FILLED.value,
            uuid.uuid4(),
            "TON_USD",
            4.970550,
            0.75,
            0.75,
            4.964925,
            0.00225,
            "TON",
            timeseries.time_now() - 3_600_000,
        )
        position_balance = PositionBalance("TON", 0.056123, 0.01, 0.0)

        can_sell, validator = is_coin_sellable(
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
            OrderStatus.ACTIVE.value,
            uuid.uuid4(),
            "TON_USD",
            4.970550,
            0.75,
            0.00,
            0.00,
            0.00,
            "TON",
            timeseries.time_now() - 3_600_000,
        )
        position_balance = PositionBalance("TON", 0.056123, 0.01, 0.0)

        can_sell, validator = is_coin_sellable(
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
            OrderStatus.ACTIVE.value,
            uuid.uuid4(),
            "TON_USD",
            4.970550,
            0.75,
            0.00,
            0.00,
            0.00,
            "TON",
            timeseries.time_now() - 3_600_000,
        )
        position_balance = PositionBalance("TON", 5.3, 0.8, 0.0)

        can_sell, validator = is_coin_sellable(
            buy_order, order_detail, position_balance
        )

        self.assertTrue(validator.order_has_not_been_filled)
        self.assertFalse(validator.wallet_balance_is_not_sufficient)
        self.assertFalse(validator.no_coin_balance)
        self.assertFalse(validator.order_has_been_cancelled)
        self.assertFalse(validator.order_balance_has_already_been_sold)
        self.assertFalse(can_sell)
