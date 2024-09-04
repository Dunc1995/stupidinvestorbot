from dataclasses import dataclass
import logging
from investorbot.constants import DEFAULT_LOGS_NAME


logger = logging.getLogger(DEFAULT_LOGS_NAME)


@dataclass
class PositionBalance:
    coin_name: str
    market_value: float
    quantity: float
    reserved_quantity: float

    @property
    def sellable_quantity(self) -> float:
        return self.quantity - self.reserved_quantity


@dataclass(init=False)
class LatestTrade:
    coin_name: str
    price: float

    def __init__(self, coin_name: str, latest_trade: float):
        self.coin_name = coin_name
        self.price = float(latest_trade)


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


@dataclass
class SaleValidationResult:
    """Contains validation checks to determine whether a coin can be sold or not. This struct can be
    used to implement different behaviors depending on what invalidates the sale for a particular
    coin."""

    no_coin_balance: bool
    order_balance_has_already_been_sold: bool
    order_has_been_cancelled: bool
    order_has_not_been_filled: bool
    wallet_balance_is_not_sufficient: bool
