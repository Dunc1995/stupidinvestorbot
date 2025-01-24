import logging
import math
import time
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
    OrderStatus,
    TrendLineState,
)
from investorbot.models import (
    BuyOrder,
    CoinSelectionCriteria,
    TimeSeriesMode,
    TimeSeriesSummary,
)
from investorbot.structs.internal import (
    OrderDetail,
    PositionBalance,
    RatingThreshold,
    SaleValidationResult,
)

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def __hours_since_order(order: OrderDetail) -> float:
    t_now = time_now()

    time_of_order = order.time_created_ms
    milliseconds_since_order = t_now - time_of_order
    return milliseconds_since_order / (1000 * 60 * 60)


def __get_minimum_acceptable_value_ratio(order: OrderDetail) -> float:
    # TODO make this configurable as DecayEquationParameters or similar. High confidence in the
    # market should result in slower decay rate.
    return 0.98 + 0.03 ** ((0.01 * __hours_since_order(order)) + 1.0)


def is_value_ratio_sufficient(value_ratio: float, order: OrderDetail) -> bool:
    return value_ratio >= __get_minimum_acceptable_value_ratio(order)


def time_now():
    return int(time.time() * 1000)


def convert_ms_time_to_hours(value: int, offset=0):
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
    trend_value = trend_line_coefficient * hour_in_time + trend_line_offset

    return trend_value


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
    coin_name: str,
    time_series_data: dict,
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

    # This algebraic expression applies this equation to all rows in the pandas DataFrame (if you're
    # not familiar with pandas).
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


def assign_weighted_rankings(
    summaries: List[TimeSeriesSummary], options: CoinSelectionCriteria
) -> int:
    for summary in summaries:
        ranking = summary.initial_ranking

        params = [
            options.coin_should_be_volatile and summary.is_volatile,
            options.coin_should_be_nominal and not summary.is_outlier_in_gradient,
            options.coin_should_be_an_outlier and summary.is_outlier_in_gradient,
            options.trend_line_should_be_falling
            and summary.trend_state == TrendLineState.FALLING.value,
            options.trend_line_should_be_flat
            and summary.trend_state == TrendLineState.FLAT.value,
            options.trend_line_should_be_rising
            and summary.trend_state == TrendLineState.RISING.value,
        ]

        for param in params:
            if param:
                ranking += 100

        summary.final_ranking = ranking

    return summaries


def is_coin_sellable(
    buy_order: BuyOrder, order_detail: OrderDetail, coin_balance: PositionBalance | None
) -> Tuple[bool, SaleValidationResult]:
    no_coin_balance = coin_balance is None or coin_balance.quantity == 0.0
    order_balance_has_already_been_sold = buy_order.sell_order is not None
    order_has_been_cancelled = order_detail.status == OrderStatus.CANCELED.value
    order_has_not_been_filled = order_detail.status != OrderStatus.COMPLETED.value
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
    ), SaleValidationResult(
        no_coin_balance,
        order_balance_has_already_been_sold,
        order_has_been_cancelled,
        order_has_not_been_filled,
        wallet_balance_is_not_sufficient,
    )
