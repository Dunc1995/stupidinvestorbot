from dataclasses import dataclass
import logging
from typing import Tuple
from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.enums import OrderStatus
from investorbot.structs.internal import (
    LatestTrade,
    OrderDetail,
    PositionBalance,
)
from investorbot.models import BuyOrder, CoinSelectionCriteria, TimeSeriesSummary
from investorbot.timeseries import get_trend_value, time_now, convert_ms_time_to_hours

logger = logging.getLogger(DEFAULT_LOGS_NAME)


@dataclass(init=False)
class LatestTradeValidator:
    latest_trade_price: float
    mean: float
    percentage_standard_deviation: float
    standard_deviation_upper_bound: float
    standard_deviation_lower_bound: float
    trend_line_coefficient: float
    trend_line_offset: float

    options: CoinSelectionCriteria

    def __init__(
        self,
        latest_trade: LatestTrade,
        time_series_summary: TimeSeriesSummary,
        validator_options: CoinSelectionCriteria,
    ):
        # TODO may need to break this down.
        self.latest_trade_price = latest_trade.price
        mean = time_series_summary.mean
        std = time_series_summary.std
        self.mean = mean
        self.percentage_standard_deviation = time_series_summary.percentage_std
        self.standard_deviation_upper_bound = mean + std
        self.standard_deviation_lower_bound = mean - std
        self.trend_line_coefficient = time_series_summary.line_of_best_fit_coefficient
        self.trend_line_offset = time_series_summary.line_of_best_fit_offset
        self.time_offset = time_series_summary.time_offset
        self.options = validator_options

    def __get_trend_value(self, hour_in_time: float) -> float:
        return get_trend_value(
            self.trend_line_coefficient, hour_in_time, self.trend_line_offset
        )

    @property
    def trend_line_price_percentage_change(self) -> float:
        now = time_now()
        hours_now = convert_ms_time_to_hours(now, self.time_offset)

        # TODO can revisit this implementation. Can probably be simplified. If using 24.0 instead of
        # hours_now then there's no need for the time_offset column in TimeSeriesSummary. Precision
        # probably isn't important here.

        # TODO Maybe include trend line percentage delta 24 hours in TimeSeriesSummary
        # (Precalculated)

        value_at_zero = self.__get_trend_value(0.0)
        value_at_now = self.__get_trend_value(hours_now)

        return (value_at_now / value_at_zero) - 1.0

    @property
    def is_trend_line_flat(self) -> bool:
        return (
            self.trend_line_price_percentage_change
            < self.options.trend_line_percentage_threshold
            and self.trend_line_price_percentage_change
            > -self.options.trend_line_percentage_threshold
        )

    @property
    def is_trend_line_rising(self) -> bool:
        return (
            self.trend_line_price_percentage_change
            >= self.options.trend_line_percentage_threshold
        )

    @property
    def is_trend_line_falling(self) -> bool:
        return (
            self.trend_line_price_percentage_change
            <= -self.options.trend_line_percentage_threshold
        )

    @property
    def is_within_lower_bound_and_mean(self) -> bool:
        return (
            self.latest_trade_price < self.mean
            and self.latest_trade_price >= self.standard_deviation_lower_bound
        )

    @property
    def is_within_upper_bound_and_mean(self) -> bool:
        # TODO don't think this is needed
        return (
            self.latest_trade_price >= self.mean
            and self.latest_trade_price <= self.standard_deviation_upper_bound
        )

    def is_valid_for_purchase(self) -> bool:
        criteria = []

        if self.options.trade_needs_to_be_within_mean_and_lower_bound:
            criteria.append(self.is_within_lower_bound_and_mean)

        if self.options.trade_needs_to_be_within_mean_and_upper_bound:
            criteria.append(self.is_within_upper_bound_and_mean)

        if self.options.trend_line_should_be_falling:
            criteria.append(self.is_trend_line_falling)

        if self.options.trend_line_should_be_flat:
            criteria.append(self.is_trend_line_flat)

        if self.options.trend_line_should_be_rising:
            criteria.append(self.is_trend_line_rising)

        if self.options.trend_line_should_be_flat_or_rising:
            criteria.append(self.is_trend_line_flat or self.is_trend_line_rising)

        if self.options.standard_deviation_threshold_should_exceed_threshold:
            criteria.append(
                self.percentage_standard_deviation
                >= self.options.standard_deviation_threshold
            )

        return all(i for i in criteria)


@dataclass
class CoinValidationResult:
    no_coin_balance: bool
    order_balance_has_already_been_sold: bool
    order_has_been_cancelled: bool
    order_has_not_been_filled: bool
    wallet_balance_is_not_sufficient: bool


def is_coin_sellable(
    buy_order: BuyOrder, order_detail: OrderDetail, coin_balance: PositionBalance | None
) -> Tuple[bool, CoinValidationResult]:

    no_coin_balance = coin_balance is None
    order_balance_has_already_been_sold = buy_order.sell_order is not None
    order_has_been_cancelled = order_detail.status == OrderStatus.CANCELED.value
    order_has_not_been_filled = order_detail.status != OrderStatus.FILLED.value
    wallet_balance_is_not_sufficient = (
        coin_balance.sellable_quantity < order_detail.order_quantity_minus_fee
        if coin_balance is not None
        else True
    )

    return not any(
        [
            no_coin_balance,
            order_balance_has_already_been_sold,
            order_has_been_cancelled,
            order_has_not_been_filled,
            wallet_balance_is_not_sufficient,
        ]
    ), CoinValidationResult(
        no_coin_balance,
        order_balance_has_already_been_sold,
        order_has_been_cancelled,
        order_has_not_been_filled,
        wallet_balance_is_not_sufficient,
    )
