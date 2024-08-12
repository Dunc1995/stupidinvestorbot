from dataclasses import dataclass
from decimal import Decimal
from pandas import Series
from investorbot.structs.ingress import PositionBalanceJson, OrderDetailJson


@dataclass
class CoinSummary:
    """Data container for storing basic statistical properties after
    analyzing valuation data for a particular coin.
    """

    name: str
    latest_trade: float
    quantity_tick_size: float
    mean_24h: float
    modes_24h: Series
    std_24h: float
    percentage_change_24h: float
    percentage_std_24h: float
    is_greater_than_mean: bool
    is_greater_than_std: bool
    __coin_quantity: float = -1.0  # TODO numerical types here are a bit muddled.

    @property
    def has_few_modes(self) -> bool:
        """Potentially useful if a low number of modes signifies a fairly stable coin resembling
        "white noise" variability.

        Returns:
            bool: True if low number of modes for the given dataset.
        """
        return len(self.modes_24h) < 5

    @property
    def has_high_std(self) -> bool:
        """Useful to work out which coins are the most volatile at any point in time.

        Returns:
            bool: True if standard deviation is higher than the given threshold.
        """
        return self.percentage_std_24h > 0.04

    @property
    def has_low_change(self) -> bool:
        """I'm assuming it's a safe assumption that a volatile coin at its mean or lower than average
        will hopefully have a rebound back to a value above its mean. Use this property to invest at the
        average price or lower.

        Returns:
            bool: True if percentage change is close to zero.
        """
        return self.percentage_change_24h < 0.03 and self.percentage_change_24h > -0.03

    def __get_coin_quantity_divisible_by_tick_size(
        self, investment_total_usd: str
    ) -> Decimal:

        _instrument_price_usd = Decimal(self.latest_trade)

        absolute_coin_quantity = Decimal(investment_total_usd) / _instrument_price_usd

        amount = Decimal(str(absolute_coin_quantity))
        tick = Decimal(str(self.quantity_tick_size))

        remainder = amount % tick

        return amount - remainder

    @property
    def coin_quantity(self) -> float:
        return self.__coin_quantity

    @coin_quantity.setter
    def coin_quantity(self, x) -> float:
        self.__coin_quantity = self.__get_coin_quantity_divisible_by_tick_size(str(x))


@dataclass(init=False)
class SellOrder:
    buy_order_status: str
    buy_order_id: str
    coin_name: str
    value_ratio: float
    original_order_value: float
    current_market_value: float
    order_quantity: float
    wallet_quantity: float
    sellable_quantity: float
    market_value_rounding: int
    coin_quantity_can_be_sold = True

    def __init__(
        self, coin_wallet_balance: PositionBalanceJson, order_detail: OrderDetailJson
    ):
        self.buy_order_status = order_detail.status
        self.buy_order_id = order_detail.client_oid
        self.coin_name = order_detail.instrument_name
        self.wallet_quantity = float(coin_wallet_balance.quantity)
        self.order_quantity = float(order_detail.quantity)
        self.original_order_value = float(order_detail.order_value)
        self.sellable_quantity = self.wallet_quantity
        self.market_value_rounding = (
            len(order_detail.order_value.split(".")[1])
            if "." in order_detail.order_value
            else 0
        )

        current_market_value = float(coin_wallet_balance.market_value)
        quantity_ratio = self.order_quantity / self.wallet_quantity

        self.current_market_value = current_market_value

        if (
            self.wallet_quantity < self.order_quantity * 0.995
            or not order_detail.successful
        ):  # 0.995 should account for any fee deductions
            self.coin_quantity_can_be_sold = False

        # if quantity after fee is larger than quantity before, then
        # then the initial buy order doesn't account for the total coin
        # quantity in the user's wallet and shouldn't attempt to sell
        # the total quantity available.
        if self.wallet_quantity > self.order_quantity:
            self.current_market_value = current_market_value * quantity_ratio
            self.sellable_quantity = self.order_quantity

        self.value_ratio = self.current_market_value / self.original_order_value
