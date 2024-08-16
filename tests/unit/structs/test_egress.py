import unittest
from investorbot.models import CoinProperties
from investorbot.structs.egress import CoinPurchase


class TestCoinPurchase(unittest.TestCase):
    def setUp(self):
        pass

    def test_coin_purchase_formatting(self):
        coin_props = CoinProperties("BTC_USD", 0.00001, 5, 0.01, 2)

        spec = CoinPurchase(coin_props, 59000.0)

        print(spec.price_per_coin)
        print(spec.quantity)

        # TODO formatting could be useful to test here. Not sure how just yet.

        self.assertEqual(spec.price_per_coin, "59000")


if __name__ == "__main__":
    unittest.main()
