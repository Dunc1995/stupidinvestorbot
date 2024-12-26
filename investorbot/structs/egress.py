from dataclasses import dataclass
import math
from investorbot.constants import INVESTMENT_INCREMENTS
from investorbot.decorators import no_scientific_notation
from investorbot.models import CoinProperties


def get_tens(decimal_places: int) -> int:
    """If 3 decimal places, return 1000, if 2 decimal_places return 10, etc. - there's probably more
    formal terminology to refer to this method, but it's used to maintain precision whilst flooring
    values according to a certain level of precision."""
    output_str = "1" + (decimal_places * "0")
    output = int(output_str)

    return output


def get_tick_quantity(
    absolute_quantity: float, coin_props: CoinProperties, is_sale: bool
) -> float | int:
    """Coin quantity needs to be specified according to a level of precision."""

    decimal_places = coin_props.quantity_decimals

    # FIXME There is probably a better name for this.
    tens = get_tens(decimal_places)

    output = None

    if decimal_places > 0 and not is_sale:
        # Values can be rounded up when purchasing coins - USD balance should always be available to
        # account for slightly higher order values.
        output = round(absolute_quantity, decimal_places)

    if decimal_places > 0 and is_sale:
        # Values always need to be rounded down when selling a coin, otherwise the application may
        # try to sell more coin than is available in the user wallet.
        output = math.floor(absolute_quantity * tens) / tens

    else:
        # Round integer values.
        output = int(
            absolute_quantity - (absolute_quantity % coin_props.quantity_tick_size)
        )

    return output


@dataclass
class CoinPurchase:
    coin_properties: CoinProperties
    __price_per_coin: float

    @property
    @no_scientific_notation
    def quantity(self) -> float | int:
        total_order_value = INVESTMENT_INCREMENTS

        absolute_quantity = total_order_value / self.__price_per_coin

        return get_tick_quantity(absolute_quantity, self.coin_properties, False)

    @property
    @no_scientific_notation
    def price_per_coin(self) -> float:
        return self.__price_per_coin


@dataclass
class CoinSale:
    coin_properties: CoinProperties
    __price_per_coin: float
    __quantity: float

    @property
    @no_scientific_notation
    def quantity(self) -> float | int:
        return get_tick_quantity(self.__quantity, self.coin_properties, True)

    @property
    @no_scientific_notation
    def price_per_coin(self) -> float:
        return round(
            self.__price_per_coin,
            self.coin_properties.price_decimals,
        )
