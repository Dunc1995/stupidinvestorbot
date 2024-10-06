import logging
import math
import time
from typing import List, Tuple
import pandas as pd
from pandas import DataFrame
import numpy as np

from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.enums import ConfidenceRating
from investorbot.models import TimeSeriesMode, TimeSeriesSummary
from investorbot.structs.internal import RatingThreshold

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def time_now():
    return int(time.time() * 1000)


def convert_ms_time_to_hours(value: int, offset=0):
    result = (value - offset) / (1000 * 60 * 60)

    return float(result)


def get_trend_value(
    trend_line_coefficient: float | DataFrame,
    hour_in_time: float,
    trend_line_offset: float | DataFrame,
) -> float | DataFrame:
    """Get coin value along a given trend line."""
    trend_value = trend_line_coefficient * hour_in_time + trend_line_offset

    return trend_value


def get_time_series_data_frame(time_series_data: dict) -> Tuple[DataFrame, int]:
    """Ingests JSON time series data in the format [{ 'v': 1.0 't': 1.0 }, ... ], converts this to a
    pandas DataFrame and formats the data so that the time axis is measured in hours as oppose to
    milliseconds.
    """
    df = pd.DataFrame.from_dict(time_series_data)

    time_value_offset = int(
        df["t"].iat[-1]
    )  # Relies on data ordered from most recent to x hours ago.

    df["t"] = df["t"].apply(
        lambda x: convert_ms_time_to_hours(x, time_value_offset)
    )  # Convert to hours.
    df["v"] = df["v"].astype(float)

    df = df[::-1]
    df.reset_index(inplace=True, drop=True)

    return df, time_value_offset


def get_line_of_best_fit(df: DataFrame):
    """Uses numpy to generate simple trend line parameters based on the input DataFrame."""

    time_array = df["t"].to_numpy()
    value_array = df["v"].to_numpy()

    a, b = np.polyfit(time_array, value_array, 1)

    return a, b


def get_coin_time_series_summary(
    coin_name: str, time_series_data: dict
) -> TimeSeriesSummary:
    """Uses pandas to get basic statistical parameters to describe the input JSON time series
    data."""

    stats, time_offset = get_time_series_data_frame(time_series_data)

    a, b = get_line_of_best_fit(stats)

    logger.debug(stats)

    mean = stats["v"].mean()
    std = stats["v"].std()
    modes = stats["v"].mode()
    starting_value = stats["v"].iloc[0]
    dataset_count = len(stats)
    percentage_std = float(std) / float(mean)

    return TimeSeriesSummary(
        coin_name=coin_name,
        mean=mean,
        modes=[TimeSeriesMode(mode=float(mode_value)) for mode_value in modes],
        std=std,
        percentage_std=percentage_std,
        line_of_best_fit_coefficient=a,
        line_of_best_fit_offset=b,
        starting_value=starting_value,
        dataset_count=dataset_count,
        time_offset=time_offset,
    )


def get_market_analysis_rating(
    ts_data: List[TimeSeriesSummary], rating_thresholds: List[RatingThreshold]
) -> ConfidenceRating:
    """For a given set of time series summaries, calculate the market trend across all coins."""

    ratings = []

    df = pd.DataFrame.from_records([ts_entry.__dict__ for ts_entry in ts_data])

    df["value_at_zero"] = get_trend_value(
        df["line_of_best_fit_coefficient"], 0.0, df["line_of_best_fit_offset"]
    )
    df["value_at_now"] = get_trend_value(
        df["line_of_best_fit_coefficient"], 24.0, df["line_of_best_fit_offset"]
    )

    # This algebraic expression applies this equation to all rows in the pandas DataFrame (if you're
    # not familiar with pandas).
    df["percentage_change"] = (df["value_at_now"] / df["value_at_zero"]) - 1.0

    median_value = df["percentage_change"].median()

    for rating_threshold in rating_thresholds:
        if rating_threshold.is_in_bounds(median_value):
            rating_id = ConfidenceRating(rating_threshold.rating_id)
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

    # flooring here to account for zero index.
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
