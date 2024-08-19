from dataclasses import dataclass
from investorbot.constants import INVESTMENT_INCREMENTS
from investorbot.decorators import no_scientific_notation
from investorbot.models import CoinProperties


def get_tick_quantity(
    absolute_quantity: float, coin_props: CoinProperties
) -> float | int:
    decimal_places = coin_props.quantity_decimals

    return (
        round(absolute_quantity, decimal_places)
        if decimal_places > 0
        else int(
            absolute_quantity - (absolute_quantity % coin_props.quantity_tick_size)
        )
    )


@dataclass
class CoinPurchase:
    coin_properties: CoinProperties
    __price_per_coin: float

    @property
    @no_scientific_notation
    def quantity(self) -> float | int:
        total_order_value = INVESTMENT_INCREMENTS

        absolute_quantity = total_order_value / self.__price_per_coin

        return get_tick_quantity(absolute_quantity, self.coin_properties)

    @property
    @no_scientific_notation
    def price_per_coin(self) -> float:
        return self.__price_per_coin


@dataclass
class CoinSale:
    coin_properties: CoinProperties
    __total_order_value: float
    __quantity: float

    @property
    @no_scientific_notation
    def quantity(self) -> float | int:
        return get_tick_quantity(self.__quantity, self.coin_properties)

    @property
    @no_scientific_notation
    def price_per_coin(self) -> float:
        # Absolute quantity can be used for division here seeing as price
        # per coin won't be affected by corrections to the CoinSale quantity.
        # Simply means the actual sale value may be slightly less than what's
        # calculated internally to trigger the initial sale. Final profit
        # will be logged once the SELL order has been filled. Coin dust
        # conversions can be used to recoup some of the lost value but this
        # has to be done manually currently :(
        return round(
            self.__total_order_value / self.__quantity,
            self.coin_properties.price_decimals,
        )
