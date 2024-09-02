from dataclasses import dataclass
import logging
import time
from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.structs.ingress import OrderDetailJson, PositionBalanceJson, TickerJson


logger = logging.getLogger(DEFAULT_LOGS_NAME)


# TODO this is here due to circular imports - needs fixing
def time_now():
    return int(time.time() * 1000)


@dataclass
class PositionBalance:
    coin_name: str
    market_value: float
    quantity: float
    reserved_quantity: float

    def from_json(balance: PositionBalanceJson) -> "PositionBalance":
        return PositionBalance(
            coin_name=balance.instrument_name,
            market_value=float(balance.market_value),
            quantity=float(balance.quantity),
            reserved_quantity=float(balance.reserved_qty),
        )

    @property
    def sellable_quantity(self) -> float:
        return self.quantity - self.reserved_quantity


@dataclass(init=False)
class LatestTrade:
    coin_name: str
    price: float

    def __init__(self, ticker: TickerJson):
        self.coin_name = ticker.instrument_name
        self.price = float(ticker.latest_trade)


@dataclass
class OrderDetail:
    status: str
    order_id: str
    coin_name: str
    order_value: float
    quantity: float
    cumulative_quantity: float
    cumulative_value: float
    cumulative_fee: float
    fee_currency: str
    time_created_ms: int

    @staticmethod
    def from_json(json_data: OrderDetailJson) -> "OrderDetail":
        return OrderDetail(
            status=json_data.status,
            order_id=json_data.client_oid,
            coin_name=json_data.instrument_name,
            order_value=float(json_data.order_value),
            quantity=float(json_data.quantity),
            cumulative_quantity=float(json_data.cumulative_quantity),
            cumulative_value=float(json_data.cumulative_value),
            cumulative_fee=float(json_data.cumulative_fee),
            fee_currency=json_data.fee_instrument_name,
            time_created_ms=int(json_data.create_time),
        )

    @property
    def hours_since_order(self) -> float:
        t_now = time_now()

        time_of_order = self.time_created_ms
        milliseconds_since_order = t_now - time_of_order
        return milliseconds_since_order / (1000 * 60 * 60)

    @property
    def minimum_acceptable_value_ratio(self) -> float:
        # TODO make this configurable as DecayEquationParameters or similar. High confidence in the
        # market should result in slower decay rate.
        return 0.98 + 0.03 ** ((0.01 * self.hours_since_order) + 1.0)

    @property
    def order_quantity_minus_fee(self) -> float:
        currency = self.coin_name.split("_")[0]

        if self.fee_currency != currency:
            logger.warn(
                f"{currency} has been used to calculate the fee for {self.coin_name}. Unable"
                + " to calculate fee deduction. You may still be able to proceed with selling this"
                + " order if your wallet balance allows."
            )

        return self.cumulative_quantity - self.cumulative_fee


@dataclass
class RatingThreshold:
    rating_id: int
    rating_upper_threshold: float
    rating_upper_unbounded: bool
    rating_lower_threshold: float
    rating_lower_unbounded: bool

    def is_in_bounds(self, value: float) -> bool:
        upper_condition = (
            value < self.rating_upper_threshold or self.rating_upper_unbounded
        )
        lower_condition = (
            value >= self.rating_lower_threshold or self.rating_lower_unbounded
        )

        return upper_condition and lower_condition
