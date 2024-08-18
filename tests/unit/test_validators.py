import json
import unittest
import uuid

from investorbot import timeseries
from investorbot.structs.internal import OrderDetail, OrderStatuses, PositionBalance
from investorbot.validators import CoinSaleValidator


class TestValidators(unittest.TestCase):
    def setUp(self):
        pass

    def get_validator(
        self, order_detail: OrderDetail, position_balance: PositionBalance
    ) -> CoinSaleValidator:
        validator = CoinSaleValidator(order_detail, position_balance)

        print(
            json.dumps(
                {
                    "minimum_acceptable_value_ratio": validator.order_detail.minimum_acceptable_value_ratio,
                    "current_value_ratio": validator.value_ratio,
                    "value_according_to_wallet": validator.current_order_value,
                    "original_order_value": validator.order_value_minus_fee,
                },
                indent=4,
            )
        )

        return validator

    def test_coin_sale_validator_will_not_sell_because_of_value_ratio(self):
        """
        Covers basis for when all criteria has been met for the bot to sell a coin.
        It's now just a case of waiting for the coin value to reach an acceptable
        value.
        """
        order_detail = OrderDetail(
            OrderStatuses.FILLED.value,
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

        validator = self.get_validator(order_detail, position_balance)

        self.assertTrue(validator.is_buy_order_complete)
        self.assertTrue(validator.is_wallet_quantity_sufficient)
        self.assertFalse(validator.is_value_ratio_sufficient)
        self.assertFalse(validator.is_valid_for_sale())

    def test_coin_sale_validator_will_sell(self):
        """
        The coin has now reached an acceptable value to sell.
        """
        order_detail = OrderDetail(
            OrderStatuses.FILLED.value,
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
        position_balance = PositionBalance("TON", 5.346032, 0.752975, 0.0)

        validator = self.get_validator(order_detail, position_balance)

        self.assertTrue(validator.is_buy_order_complete)
        self.assertTrue(validator.is_wallet_quantity_sufficient)
        self.assertTrue(validator.is_value_ratio_sufficient)
        self.assertTrue(validator.is_valid_for_sale())

    def test_coin_sale_validator_will_not_sell_because_of_wallet_quantity(self):
        """
        A user may sell a coin manually, causing the original order quantity to
        be higher than what exists in the user's wallet. The bot needs to handle
        this gracefully.
        """
        order_detail = OrderDetail(
            OrderStatuses.FILLED.value,
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

        validator = self.get_validator(order_detail, position_balance)

        self.assertTrue(validator.is_buy_order_complete)
        self.assertFalse(validator.is_wallet_quantity_sufficient)
        self.assertFalse(validator.is_value_ratio_sufficient)
        self.assertFalse(validator.is_valid_for_sale())

    def test_coin_sale_validator_will_not_break_on_small_coin_balance(self):
        """
        A user may have a small amount of coin available whilst they have a pending
        buy order. This needs to be handled gracefully by the validator.
        """
        order_detail = OrderDetail(
            OrderStatuses.ACTIVE.value,
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

        validator = self.get_validator(order_detail, position_balance)

        self.assertFalse(validator.is_buy_order_complete)
        self.assertFalse(validator.is_wallet_quantity_sufficient)
        self.assertFalse(validator.is_value_ratio_sufficient)
        self.assertFalse(validator.is_valid_for_sale())

    def test_coin_sale_validator_will_not_break_on_normal_coin_balance(self):
        """
        A user may have an amount of coin available whilst they have a pending
        buy order. This needs to be handled gracefully by the validator.
        """
        order_detail = OrderDetail(
            OrderStatuses.ACTIVE.value,
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

        validator = self.get_validator(order_detail, position_balance)

        self.assertAlmostEqual(validator.order_value_minus_fee, 0.0)
        self.assertFalse(validator.is_buy_order_complete)
        self.assertTrue(validator.is_wallet_quantity_sufficient)
        self.assertFalse(validator.is_value_ratio_sufficient)
        self.assertFalse(validator.is_valid_for_sale())
