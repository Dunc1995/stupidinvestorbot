import json
import time
import unittest
import uuid

from investorbot.structs.ingress import InstrumentJson
from investorbot.repo import InvestorBotRepo
from investorbot.models import BuyOrder
import investorbot.structs.transforms as transforms


class TestInvestorBotRepo(unittest.TestCase):
    def setUp(self):
        instrument_data = None

        self.test_context = InvestorBotRepo("sqlite:///:memory:")
        self.test_context.run_migration()

        with open("./tests/integration/fixtures/get-instruments.json", "r") as f:
            instrument_data = json.loads(f.read())["result"]["data"]

        instruments = [InstrumentJson(**inst_data) for inst_data in instrument_data]
        coin_properties = transforms.get_coin_properties_from_instruments(instruments)

        self.test_context.add_items(coin_properties)

    def test_get_buy_order_will_return_none(self):
        result = self.test_context.get_buy_order("123")

        self.assertIsNone(result, "Buy order query result is not None.")

    def test_buy_order_can_be_stored_and_retrieved(self):
        buy_order_id = str(uuid.uuid4())

        buy_order = BuyOrder(buy_order_id=buy_order_id, coin_name="AGLD_USDT")
        self.test_context.add_item(buy_order)

        db_buy_order = self.test_context.get_buy_order(buy_order_id)

        self.assertEqual(db_buy_order.buy_order_id, buy_order_id)
        self.assertIsInstance(
            db_buy_order.coin_properties.price_decimals,
            int,
            "Decimal place count must be an integer.",
        )
        self.assertIsInstance(
            db_buy_order.coin_properties.price_tick_size,
            float,
            "Tick size must be a float.",
        )
        self.assertIsInstance(
            db_buy_order.coin_properties.quantity_decimals,
            int,
            "Decimal value must be an integer.",
        )
        self.assertIsInstance(
            db_buy_order.coin_properties.quantity_tick_size,
            float,
            "Tick size must be a float.",
        )


if __name__ == "__main__":
    unittest.main()
