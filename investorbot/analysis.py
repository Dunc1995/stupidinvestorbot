"""Statistical analysis for time series data.

This module contains pure statistical functions that operate on canonical TimeSeries data.
Business/trading logic (sell validation, weighted rankings) lives in investorbot.strategy.
"""

import logging
import math
from typing import List, Tuple
import pandas as pd
from pandas import DataFrame
import numpy as np

from investorbot.constants import (
    DEFAULT_LOGS_NAME,
    INVESTOR_APP_FLATNESS_THRESHOLD,
    INVESTOR_APP_VOLATILITY_THRESHOLD,
)
from investorbot.enums import (
    MarketCharacterization,
    TrendLineState,
)
from investorbot.models import (
    CoinSelectionCriteria,
    TimeSeriesMode,
    TimeSeriesSummary,
)
from investorbot.structs.internal import (
    RatingThreshold,
    TimeSeriesPoint,
    TimeSeries,
)

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def convert_ms_time_to_hours(value: int, offset=0) -> float:
    result = (value - offset) / (1000 * 60 * 60)
    return float(result)


def ts_data_count_to_hours(data_count: int) -> float:
    return float((24 / 2880) * data_count)


def get_trend_value(
    trend_line_coefficient: float | DataFrame,
    hour_in_time: float,
    trend_line_offset: float | DataFrame,
) -> float | DataFrame:
    """Get coin value along a given trend line."""
    return trend_line_coefficient * hour_in_time + trend_line_offset


def get_trend_line_price_percentage_change(
    normalized_gradient: float, data_count: int
) -> float:
    hours = ts_data_count_to_hours(data_count)
    value_at_now = get_trend_value(normalized_gradient, hours, 1)
    return (value_at_now) - 1.0


def get_trend_line_state(trend_line_price_percentage_change: float) -> str:
    state = TrendLineState.UNKNOWN

    if (
        trend_line_price_percentage_change < INVESTOR_APP_FLATNESS_THRESHOLD
        and trend_line_price_percentage_change > -INVESTOR_APP_FLATNESS_THRESHOLD
    ):
        state = TrendLineState.FLAT
    elif trend_line_price_percentage_change >= INVESTOR_APP_FLATNESS_THRESHOLD:
        state = TrendLineState.RISING
    elif trend_line_price_percentage_change <= -INVESTOR_APP_FLATNESS_THRESHOLD:
        state = TrendLineState.FALLING

    return state.value


def time_series_to_data_frame(time_series: TimeSeries) -> Tuple[DataFrame, int]:
    """Convert canonical TimeSeries data into a pandas DataFrame with time in hours.

    Accepts the canonical List[TimeSeriesPoint] format. Data is expected to be ordered from most
    recent to oldest (matching the Crypto.com API convention). The function reverses this to
    chronological order.
    """
    records = [{"t": point.timestamp_ms, "v": point.value} for point in time_series]
    df = pd.DataFrame.from_records(records)

    time_value_offset = int(df["t"].iat[-1])

    df["t"] = df["t"].apply(lambda x: convert_ms_time_to_hours(x, time_value_offset))
    df["v"] = df["v"].astype(float)

    df = df[::-1]
    df.reset_index(inplace=True, drop=True)

    return df, time_value_offset


# Keep the old name as an alias for backward compatibility with tests that use raw dicts.
def get_time_series_data_frame(time_series_data: dict | list) -> Tuple[DataFrame, int]:
    """Legacy adapter: accepts raw dict/list format (e.g. [{'v': 1.0, 't': 1.0}, ...]) and
    converts to DataFrame. Prefer time_series_to_data_frame() for new code."""
    if isinstance(time_series_data, list) and len(time_series_data) > 0:
        if isinstance(time_series_data[0], TimeSeriesPoint):
            return time_series_to_data_frame(time_series_data)

    # Legacy path: raw dict/list from Crypto.com API format.
    df = pd.DataFrame.from_dict(time_series_data)

    time_value_offset = int(df["t"].iat[-1])

    df["t"] = df["t"].apply(lambda x: convert_ms_time_to_hours(x, time_value_offset))
    df["v"] = df["v"].astype(float)

    df = df[::-1]
    df.reset_index(inplace=True, drop=True)

    return df, time_value_offset


def get_line_of_best_fit(df: DataFrame) -> Tuple[float, float]:
    """Uses numpy to generate simple trend line parameters based on the input DataFrame."""
    time_array = df["t"].to_numpy()
    value_array = df["v"].to_numpy()

    a, b = np.polyfit(time_array, value_array, 1)

    return a, b


def get_coin_time_series_summary(
    coin_name: str,
    time_series_data: dict | TimeSeries,
) -> TimeSeriesSummary:
    """Calculate statistical summary for a coin's time series data.

    Accepts either the canonical TimeSeries format or the legacy dict format for backward
    compatibility.
    """
    stats, time_offset = get_time_series_data_frame(time_series_data)

    a, b = get_line_of_best_fit(stats)

    logger.debug(stats)

    mean = stats["v"].mean()
    std = stats["v"].std()
    modes = stats["v"].mode()
    starting_value = stats["v"].iloc[0]
    dataset_count = len(stats)

    normalized_line_of_best_fit_coefficient = a / b
    normalized_starting_value = starting_value / b
    normalized_std = float(std) / float(mean)
    is_volatile = (
        normalized_std >= INVESTOR_APP_VOLATILITY_THRESHOLD
        or normalized_std <= -INVESTOR_APP_VOLATILITY_THRESHOLD
    )

    trend_line_percentage_change = get_trend_line_price_percentage_change(
        normalized_line_of_best_fit_coefficient, dataset_count
    )

    return TimeSeriesSummary(
        coin_name=coin_name,
        mean=mean,
        modes=[TimeSeriesMode(mode=float(mode_value)) for mode_value in modes],
        std=std,
        line_of_best_fit_coefficient=a,
        line_of_best_fit_offset=b,
        starting_value=starting_value,
        normalized_line_of_best_fit_coefficient=normalized_line_of_best_fit_coefficient,
        normalized_starting_value=normalized_starting_value,
        normalized_std=normalized_std,
        trend_state=get_trend_line_state(trend_line_percentage_change),
        is_volatile=is_volatile,
        dataset_count=dataset_count,
        time_offset=time_offset,
    )


def get_market_analysis_rating(
    ts_data: List[TimeSeriesSummary], rating_thresholds: List[RatingThreshold]
) -> MarketCharacterization:
    """For a given set of time series summaries, calculate the market trend across all coins."""

    ratings = []

    df = pd.DataFrame.from_records([ts_entry.__dict__ for ts_entry in ts_data])

    df["value_at_zero"] = get_trend_value(
        df["line_of_best_fit_coefficient"], 0.0, df["line_of_best_fit_offset"]
    )

    # TODO don't hardcode 24 hours here
    df["value_at_now"] = get_trend_value(
        df["line_of_best_fit_coefficient"], 24.0, df["line_of_best_fit_offset"]
    )

    df["percentage_change"] = (df["value_at_now"] / df["value_at_zero"]) - 1.0

    median_value = df["percentage_change"].median()

    for rating_threshold in rating_thresholds:
        if rating_threshold.is_in_bounds(median_value):
            rating_id = MarketCharacterization(rating_threshold.rating_id)
            ratings.append(rating_id)

    if len(ratings) > 1:
        raise NotImplementedError(
            "More than one rating was found for a particular market analysis. "
            + "Try reconfiguring threshold values in the CoinSelectionCriteria table."
        )

    return ratings[0]


def get_outliers_in_time_series_data(
    ts_data: List[TimeSeriesSummary], property_to_check: str, value_to_set: str
) -> List[TimeSeriesSummary]:

    ordered_data = list(sorted(ts_data, key=lambda x: getattr(x, property_to_check)))

    ts_count = len(ordered_data)

    first_quartile_index = math.floor(0.25 * ts_count)
    third_quartile_index = math.floor(0.75 * ts_count)

    first_quartile = getattr(ordered_data[first_quartile_index], property_to_check)
    third_quartile = getattr(ordered_data[third_quartile_index], property_to_check)

    inter_quartile_range = third_quartile - first_quartile

    lower_boundary = first_quartile - 1.5 * inter_quartile_range
    upper_boundary = third_quartile + 1.5 * inter_quartile_range

    for data in ordered_data:
        if (
            getattr(data, property_to_check) > upper_boundary
            or getattr(data, property_to_check) < lower_boundary
        ):
            setattr(data, value_to_set, True)

    return ordered_data


def assign_outlier_properties(
    ts_summaries: TimeSeriesSummary,
) -> List[TimeSeriesSummary]:
    ts_summaries_first_iter = get_outliers_in_time_series_data(
        ts_summaries,
        TimeSeriesSummary.normalized_line_of_best_fit_coefficient.key,
        TimeSeriesSummary.is_outlier_in_gradient.key,
    )

    ts_summaries_second_iter = get_outliers_in_time_series_data(
        ts_summaries_first_iter,
        TimeSeriesSummary.normalized_starting_value.key,
        TimeSeriesSummary.is_outlier_in_offset.key,
    )

    gradient_outliers = [
        ts_summary
        for ts_summary in ts_summaries_second_iter
        if ts_summary.is_outlier_in_gradient
    ]
    deviation_candidates = [
        ts_summary
        for ts_summary in ts_summaries_second_iter
        if not ts_summary.is_outlier_in_gradient
    ]

    deviation_subset = get_outliers_in_time_series_data(
        deviation_candidates,
        TimeSeriesSummary.normalized_std.key,
        TimeSeriesSummary.is_outlier_in_deviation.key,
    )

    return gradient_outliers + deviation_subset
