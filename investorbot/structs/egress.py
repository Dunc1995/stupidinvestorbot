from dataclasses import dataclass
from investorbot.constants import INVESTMENT_INCREMENTS
from investorbot.decorators import no_scientific_notation
from investorbot.models import CoinProperties


@dataclass
class CoinPurchase:
    coin_properties: CoinProperties
    __price_per_coin: float

    @property
    @no_scientific_notation
    def quantity(self) -> float | int:
        total_order_value = INVESTMENT_INCREMENTS
        decimal_places = self.coin_properties.quantity_decimals

        absolute_quantity = total_order_value / self.__price_per_coin

        rounded_quantity = (
            round(absolute_quantity, decimal_places)
            if decimal_places > 0
            else int(
                absolute_quantity
                - (absolute_quantity % self.coin_properties.quantity_tick_size)
            )
        )

        return rounded_quantity

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
        return self.__quantity

    @property
    @no_scientific_notation
    def price_per_coin(self) -> float:
        return round(self.__price_per_coin * 1.2, self.coin_properties.price_decimals)
