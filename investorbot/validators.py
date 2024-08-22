from dataclasses import dataclass
import json
import logging
from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.structs.internal import (
    LatestTrade,
    OrderDetail,
    OrderStatuses,
    PositionBalance,
)
from investorbot.models import CoinProperties, CoinSelectionCriteria, TimeSeriesSummary
from investorbot.timeseries import time_now, convert_ms_time_to_hours

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
        trend_value = (
            self.trend_line_coefficient * hour_in_time + self.trend_line_offset
        )

        return trend_value

    @property
    def trend_line_price_percentage_change(self) -> float:
        now = time_now()
        hours_now = convert_ms_time_to_hours(now, self.time_offset)

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


@dataclass(init=False)
class CoinSaleValidator:
    order_detail: OrderDetail
    position_balance: PositionBalance

    def __init__(self, order_detail: OrderDetail, position_balance: PositionBalance):
        self.order_detail = order_detail
        self.position_balance = position_balance

    @property
    def is_buy_order_complete(self) -> bool:
        return self.order_detail.status == OrderStatuses.FILLED.value

    @property
    def wallet_market_value(self) -> float:
        return self.position_balance.market_value

    @property
    def order_quantity_minus_fee(self) -> float:
        return self.order_detail.cumulative_quantity - self.order_detail.cumulative_fee

    @property
    def order_value(self) -> float:
        return self.order_detail.cumulative_value

    @property
    def sellable_quantity(self) -> float:
        return self.position_balance.quantity - self.position_balance.reserved_quantity

    @property
    def order_quantity_as_percentage_of_wallet_quantity(self) -> float:
        if self.position_balance.quantity <= 0.000000000001:
            return -1.0

        return self.order_quantity_minus_fee / self.position_balance.quantity

    @property
    def is_wallet_quantity_sufficient(self) -> bool:

        currency = self.order_detail.coin_name.split("_")[0]

        if self.order_detail.fee_currency != currency:
            raise NotImplementedError(
                f"App canny handle fee in {self.order_detail.fee_currency} currency for {currency} order."
            )

        return self.sellable_quantity >= self.order_quantity_minus_fee

    @property
    def order_market_value(self) -> float:
        return (
            self.order_quantity_as_percentage_of_wallet_quantity
            * self.position_balance.market_value
        )

    @property
    def value_ratio(self) -> float:
        if self.order_value <= 0.000000000001:
            return -1.0

        return self.order_market_value / self.order_value

    @property
    def is_value_ratio_sufficient(self) -> bool:
        return self.value_ratio >= self.order_detail.minimum_acceptable_value_ratio

    def is_valid_for_sale(self) -> bool:
        result = True

        if not self.is_buy_order_complete:
            logger.info(f"Buy order {self.order_detail.order_id} is not complete.")
            return False

        if not self.is_wallet_quantity_sufficient:
            logger.warn(
                f"Wallet quantity not sufficient for selling order {self.order_detail.order_id}."
            )
            return False

        if not self.is_value_ratio_sufficient:
            logger.info(
                f"Value ratio is insufficient for order {self.order_detail.order_id}."
            )
            return False

        return result
