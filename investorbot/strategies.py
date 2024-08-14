from dataclasses import dataclass
from enum import Enum
from investorbot.structs.internal import LatestTrade
from investorbot.models import TimeSeriesSummary
from investorbot.timeseries import convert_ms_time_to_hours


@dataclass
class LatestTradeValidatorOptions:
    trade_needs_to_be_within_mean_and_upper_bound: bool = False
    trade_needs_to_be_within_mean_and_lower_bound: bool = False
    data_gradient_24h_should_be_flat: bool = False
    data_gradient_24h_should_be_rising: bool = False
    data_gradient_24h_should_be_falling: bool = False


@dataclass(init=False)
class LatestTradeValidator:
    latest_trade_price: float
    mean: float
    standard_deviation_upper_bound: float
    standard_deviation_lower_bound: float

    # TODO needs extra ts analysis here - use numpy to get line of best fit
    is_24h_gradient_flat: bool
    is_24h_gradient_rising: bool
    is_24h_gradient_falling: bool

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

        # TODO implement this.
        self.is_24h_gradient_flat = False
        self.is_24h_gradient_rising = False
        self.is_24h_gradient_falling = False

        self.options = validator_options

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
            criteria.append(self.is_24h_gradient_falling)

        if self.options.data_gradient_24h_should_be_flat:
            criteria.append(self.is_24h_gradient_flat)

        if self.options.data_gradient_24h_should_be_rising:
            criteria.append(self.is_24h_gradient_rising)

        return all(i for i in criteria)
