from dataclasses import dataclass
from investorbot.constants import INVESTMENT_INCREMENTS
from investorbot.decorators import formatted_numeric
from investorbot.models import CoinProperties


@dataclass
class CoinPurchase:
    coin_properties: CoinProperties
    __price_per_coin: float

    @property
    @formatted_numeric
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
    @formatted_numeric
    def price_per_coin(self) -> float:
        return self.__price_per_coin
