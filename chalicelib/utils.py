from decimal import *
import logging


logger = logging.getLogger("client")


def correct_coin_quantity(amount: str, tick: str) -> Decimal:
    """
    Precise amounts can cause the Crypto API to complain -
    this corrects the amount using the input tick value.
    """

    _amount = Decimal(str(amount))
    _tick = Decimal(str(tick))

    remainder = _amount % _tick

    return _amount - remainder


def get_coin_quantity(
    instrument_price_usd: str, investment_total_usd: str, tick: str
) -> Decimal:
    _instrument_price_usd = Decimal(instrument_price_usd)

    absolute_quantity = Decimal(investment_total_usd) / _instrument_price_usd

    return correct_coin_quantity(absolute_quantity, tick)
