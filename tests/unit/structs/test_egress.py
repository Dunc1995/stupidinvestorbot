import unittest

from investorbot.models import CoinProperties
from investorbot.structs.egress import CoinSale


class TestCoinSale(unittest.TestCase):
    """The Crypto API expects quantity and order values to be rounded to specific
    decimal places when placing orders. These test cases ensure that order values
    will be printed correctly whilst making POST requests to the Crypto API.
    """

    def setUp(self):
        pass

    def test_coin_sale_returns_correct_values_case_one(self):
        coin_properties = CoinProperties("TON_USD", 0.01, 2, 0.0001, 4)
        coin_sale = CoinSale(coin_properties, 6, 0.75)

        self.assertEqual(coin_sale.quantity, "0.75")
        self.assertEqual(coin_sale.price_per_coin, "8.0")

    def test_coin_sale_returns_correct_values_case_two(self):
        coin_properties = CoinProperties("TON_USD", 0.01, 2, 0.0001, 4)
        coin_sale = CoinSale(coin_properties, 30.3643, 5.3432)

        self.assertEqual(coin_sale.quantity, "5.34")
        self.assertEqual(coin_sale.price_per_coin, "5.6828")

    def test_coin_sale_returns_correct_values_case_three(self):
        coin_properties = CoinProperties("SOME_RANDOM_COIN", 100, 0, 0.000001, 6)
        coin_sale = CoinSale(coin_properties, 10.716, 765432.1)

        self.assertEqual(coin_sale.quantity, "765400")
        self.assertEqual(coin_sale.price_per_coin, "0.000014")
