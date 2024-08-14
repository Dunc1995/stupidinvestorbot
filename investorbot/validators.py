from dataclasses import dataclass
from investorbot.structs.internal import LatestTrade
from investorbot.models import TimeSeriesSummary
from investorbot.timeseries import time_now, convert_ms_time_to_hours


@dataclass
class LatestTradeValidatorOptions:
    trade_needs_to_be_within_mean_and_upper_bound: bool = False
    trade_needs_to_be_within_mean_and_lower_bound: bool = False
    data_gradient_24h_percentage_threshold: float = 0.01
    data_gradient_24h_should_be_flat: bool = False
    data_gradient_24h_should_be_rising: bool = False
    data_gradient_24h_should_be_falling: bool = False


@dataclass(init=False)
class LatestTradeValidator:
    latest_trade_price: float
    mean: float
    standard_deviation_upper_bound: float
    standard_deviation_lower_bound: float

    trend_line_coefficient: float
    trend_line_offset: float

    options: LatestTradeValidatorOptions

    def __init__(
        self,
        latest_trade: LatestTrade,
        time_series_summary: TimeSeriesSummary,
        validator_options: LatestTradeValidatorOptions,
    ):
        self.latest_trade_price = latest_trade.price
        mean = time_series_summary.mean
        std = time_series_summary.std
        self.mean = mean
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
            < self.options.data_gradient_24h_percentage_threshold
            and self.trend_line_price_percentage_change
            > -self.options.data_gradient_24h_percentage_threshold
        )

    @property
    def is_trend_line_rising(self) -> bool:
        return (
            self.trend_line_price_percentage_change
            >= self.options.data_gradient_24h_percentage_threshold
        )

    @property
    def is_trend_line_falling(self) -> bool:
        return (
            self.trend_line_price_percentage_change
            <= -self.options.data_gradient_24h_percentage_threshold
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

        if self.options.data_gradient_24h_should_be_falling:
            criteria.append(self.is_trend_line_falling)

        if self.options.data_gradient_24h_should_be_flat:
            criteria.append(self.is_trend_line_flat)

        if self.options.data_gradient_24h_should_be_rising:
            criteria.append(self.is_trend_line_rising)

        return all(i for i in criteria)
