from dataclasses import dataclass
from decimal import Decimal
import time
from pandas import Series
from investorbot.structs.ingress import PositionBalanceJson, OrderDetailJson


@dataclass
class TimeSeriesSummary:
    """Data container for storing basic statistical properties after
    analyzing valuation data for a particular coin.
    """

    coin_name: str
    mean: float
    modes: Series
    std: float
    percentage_std: float
    creation_time_ms: int


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


@dataclass(init=False)
class OrderDetail:
    status: str
    order_id: str
    coin_name: str
    quantity: float
    value_after_fee: float
    time_created_ms: int

    def __init__(self, json_data: OrderDetailJson):
        self.status = json_data.status
        self.order_id = json_data.client_oid
        self.coin_name = json_data.instrument_name
        self.quantity = float(json_data.cumulative_quantity)
        self.value_after_fee = float(json_data.cumulative_value) - float(
            json_data.cumulative_fee
        )
        self.time_created_ms = int(json_data.create_time)

    @property
    def hours_since_order(self) -> float:
        time_now = int(time.time() * 1000)

        time_of_order = self.time_created_ms
        milliseconds_since_order = time_now - time_of_order
        return milliseconds_since_order / (1000 * 60 * 60)

    @property
    def minimum_acceptable_value_ratio(self) -> float:
        return 0.98 + 0.03 ** ((0.01 * self.hours_since_order) + 1.0)
