import unittest

from investorbot.models import CoinProperties
from investorbot.structs.egress import CoinSale

__doc__ = """The Crypto API expects quantity and order values to be rounded to specific
decimal places when placing orders. These test cases ensure that order values will be printed
correctly whilst making POST requests to the Crypto API.
"""


def test_coin_sale_returns_correct_values_case_one():
    coin_properties = CoinProperties("TON_USD", 0.01, 2, 0.0001, 4)
    coin_sale = CoinSale(coin_properties, 8.0, 0.75)

    assert coin_sale.quantity == "0.75"
    assert coin_sale.price_per_coin == "8.0"


def test_coin_sale_returns_correct_values_case_two():
    coin_properties = CoinProperties("TON_USD", 0.01, 2, 0.0001, 4)
    coin_sale = CoinSale(coin_properties, 30.3643, 5.3432)

    assert coin_sale.quantity == "5.34"
    assert coin_sale.price_per_coin == "30.3643"


def test_coin_sale_returns_correct_values_case_three():
    coin_properties = CoinProperties("SOME_RANDOM_COIN", 100, 0, 0.000001, 6)
    coin_sale = CoinSale(coin_properties, 0.000014, 765432.1)

    assert coin_sale.quantity == "765400"
    assert coin_sale.price_per_coin == "0.000014"


def test_coin_sale_returns_correct_values_case_four():
    coin_properties = CoinProperties("AAVE_USD", 0.001, 3, 0.001, 3)
    coin_sale = CoinSale(coin_properties, 369.0, 0.0269325)

    assert coin_sale.quantity == "0.026"
    assert coin_sale.price_per_coin == "369.0"
