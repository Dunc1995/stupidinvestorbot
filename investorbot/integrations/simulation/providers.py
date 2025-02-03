from datetime import datetime, timedelta
import logging
import time
from typing import List, Tuple
import numpy as np
import pandas as pd
from pandas import DataFrame

from investorbot import env
from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.integrations.simulation.data.tickers import TICKERS
from investorbot.integrations.simulation.interfaces import (
    IDataProvider,
    ITimeSimulation,
)
from investorbot.structs.internal import LatestTrade

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def get_first_row() -> dict:
    return {x["i"]: x["a"] for x in TICKERS}


class SimulatedTimeProvider(ITimeSimulation):
    start_time: datetime
    now_time: datetime
    increment: timedelta

    def __init__(self, time_offset=timedelta(days=1), increment=timedelta(seconds=20)):
        self.start_time = datetime.now() - time_offset
        self.now_time = self.start_time
        self.increment = increment

    def now(self) -> datetime:
        return self.now_time

    def now_in_ms(self) -> int:
        return int(self.now_time.timestamp()) * 1000

    def increment_time(self) -> datetime:
        self.now_time += self.increment
        return self.now_time


class DataProvider(IDataProvider):
    time_series_data: DataFrame
    """Cached market value history. Used to fetch timeseries data."""

    rng = None
    """Random number generator."""

    seed = None
    """Random number generator seed."""

    current_ticker_values: Tuple[dict, datetime] = None
    """Current ticker values reflect the most up-to-date values for all coins on the market."""

    trend_percentage = 0.0
    """Used for generating an overall market trend whilst generating random coin values."""

    def __init__(self, seed: int, generate_static_data=False):
        self.seed = seed
        self.rng = np.random.default_rng(seed=seed)
        self.start_time = env.time.now_in_ms()
        self.current_ticker_values = {
            ticker["i"]: ticker["a"] for ticker in TICKERS
        }, self.start_time

        if generate_static_data:
            logger.info(
                "As this is a static data provider, let's generate some static data."
            )
            self.run_in_real_time(steps=1)

    def roll_dice(self) -> float:
        return self.rng.integers(low=1, high=6, endpoint=True, size=4).mean()

    def trend_updater(self):
        """This method allows for simulating a shift in overall market trends. Implementing this
        method means there's a slight chance that the overall market trend will either increase all
        coin values over time or decrease coin values over time."""

        trend_percentage = self.trend_percentage
        dice_roll = self.roll_dice()

        if dice_roll > 4.5:
            logger.info(
                f"Market trend increase - change now trending at {self.trend_percentage}%"
            )
            if trend_percentage < 0.0:
                trend_percentage = 0.0

            self.trend_percentage += 0.00002
        elif dice_roll < 2.5:
            logger.info(
                f"Market trend decrease - change now trending at {self.trend_percentage}%"
            )
            if trend_percentage > 0.0:
                trend_percentage = 0

            self.trend_percentage -= 0.00002
        else:
            logger.info(f"Market change trending at {self.trend_percentage}%")

    def get_random_value(self, mean, st_deviation):
        """Generate random values based on normal distribution."""
        return np.random.normal(loc=mean, scale=st_deviation)

    def increment_ts_data(self) -> DataFrame:
        """Updates self.current_ticker_values and returns corresponding DataFrame to append to cached
        time series data."""

        current_ticker_values = self.current_ticker_values[0]
        trend_percentage = self.trend_percentage

        sigma = 0.0004  # standard deviation

        for coin_name in current_ticker_values.keys():
            s = self.get_random_value(trend_percentage, sigma)

            new_price = float(current_ticker_values[coin_name]) * (1 + s)
            current_ticker_values[coin_name] = new_price

        current_time = env.time.now_in_ms()

        self.current_ticker_values = current_ticker_values, current_time

        df = pd.DataFrame(current_ticker_values, index=[current_time])
        df.index.name = "t"
        return df

    def get_latest_trade(self, coin_name: str) -> LatestTrade:
        return LatestTrade(coin_name, self.current_ticker_values[0][coin_name])

    def get_latest_trades(self) -> List[LatestTrade]:
        return [
            LatestTrade(coin_name, self.current_ticker_values[0][coin_name])
            for coin_name in self.current_ticker_values[0].keys()
        ]

    def get_coin_time_series_data(self, coin_name: str) -> dict:
        # TODO:
        #       converting DataFrame to List[dict] seems a bit superfluous here - this is a hangup
        #       from the application being designed around the Crypto.com API - can most likely be
        #       simplified.

        coin_data = self.time_series_data[coin_name]
        coin_data = [{"t": x, "v": y} for x, y in zip(coin_data.index, coin_data)]

        # TODO make investorbot intelligent enough to recognize ordering of data rather than
        # reversing here.
        coin_data.reverse()

        return coin_data

    def run_in_real_time(self, steps=3600):
        i = 0

        initial_data = get_first_row()
        time_series_data = pd.DataFrame(initial_data, index=[self.start_time])
        time_series_data.index.name = "t"
        self.time_series_data = time_series_data

        if not isinstance(env.time, ITimeSimulation):
            raise NotImplementedError(
                "Tried incrementing time whilst running in realtime."
            )

        # TODO make i values configurable
        while i < (steps + 2880):
            current_time = env.time.increment_time()
            new_values = self.increment_ts_data()

            # TODO could end up being a performance bottleneck here.
            self.time_series_data = pd.concat([self.time_series_data, new_values])

            if i % 10 == 0:
                self.trend_updater()

            logger.info(current_time)

            # After 2880 there's enough data to run an initial market analysis so after 2880 run the
            # simulation as though it's generating realtime data.
            if i > 2880:
                if i <= 2881:
                    logger.info("Finished generating initial market data!")
                time.sleep(1)

            i += 1
