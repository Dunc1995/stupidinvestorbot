from dataclasses import dataclass
from enum import Enum
from investorbot.timeseries import time_now
from investorbot.structs.ingress import OrderDetailJson, PositionBalanceJson, TickerJson


@dataclass(init=False)
class PositionBalance:

    def __init__(self, balance: PositionBalanceJson):
        self.market_value = balance.market_value
        self.quantity = balance.quantity


@dataclass(init=False)
class LatestTrade:
    coin_name: str
    price: float

    def __init__(self, ticker: TickerJson):
        self.coin_name = ticker.instrument_name
        self.price = float(ticker.latest_trade)


class OrderStatuses(Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    FILLED = "FILLED"
    EXPIRED = "EXPIRED"


@dataclass(init=False)
class OrderDetail:
    status: str
    order_id: str
    coin_name: str
    quantity: float
    order_value: float
    quantity: float
    cumulative_quantity: float
    cumulative_value: float
    cumulative_fee: float
    time_created_ms: int

    def __init__(self, json_data: OrderDetailJson):
        self.status = json_data.status
        self.order_id = json_data.client_oid
        self.coin_name = json_data.instrument_name
        self.order_value = float(json_data.order_value)
        self.quantity = float(json_data.quantity)
        self.cumulative_quantity = float(json_data.cumulative_quantity)
        self.cumulative_value = float(json_data.cumulative_value)
        self.cumulative_fee = float(json_data.cumulative_fee)
        self.fee_currency = json_data.fee_instrument_name
        self.time_created_ms = int(json_data.create_time)

    @property
    def hours_since_order(self) -> float:
        t_now = time_now()

        time_of_order = self.time_created_ms
        milliseconds_since_order = t_now - time_of_order
        return milliseconds_since_order / (1000 * 60 * 60)

    @property
    def minimum_acceptable_value_ratio(self) -> float:
        return 0.98 + 0.03 ** ((0.01 * self.hours_since_order) + 1.0)
