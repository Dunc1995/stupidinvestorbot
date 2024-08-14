import logging
import time
import pandas as pd
from pandas import DataFrame
import numpy as np
import datetime as dt

from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.models import TimeSeriesMode, TimeSeriesSummary

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def get_time_series_data_frame(time_series_data: dict) -> DataFrame:
    df = pd.DataFrame.from_dict(time_series_data)

    time_value_offset = df["t"].iat[-1]

    df["t"] = df["t"].apply(
        lambda x: (x - time_value_offset) / (1000 * 60 * 60)
    )  # Convert to hours.
    df["v"] = df["v"].astype(float)

    df = df[::-1]
    df.reset_index(inplace=True, drop=True)

    return df


def get_line_of_best_fix(df: DataFrame):
    time_array = df["t"].to_numpy()
    value_array = df["v"].to_numpy()

    a, b = np.polyfit(time_array, value_array, 1)

    return a, b


def get_coin_time_series_summary(
    coin_name: str, time_series_data: dict
) -> TimeSeriesSummary:

    stats = get_time_series_data_frame(time_series_data)

    a, b = get_line_of_best_fix(stats)

    logger.debug(stats)

    mean = stats["v"].mean()
    std = stats["v"].std()
    modes = stats["v"].mode()
    percentage_std = float(std) / float(mean)

    return TimeSeriesSummary(
        coin_name=coin_name,
        mean=mean,
        modes=[TimeSeriesMode(mode=float(mode_value)) for mode_value in modes],
        std=std,
        percentage_std=percentage_std,
        line_of_best_fit_coefficient=a,
        line_of_best_fit_offset=b,
        creation_time_ms=int(time.time() * 1000),
    )
