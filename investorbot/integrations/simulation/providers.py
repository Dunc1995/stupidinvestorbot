from datetime import datetime
from os import path
import time
from typing import List, Tuple
import numpy as np
import pandas as pd
from pandas import DataFrame

from investorbot.integrations.simulation.constants import TIME_SERIES_DATA_PATH
from investorbot.integrations.simulation.data.tickers import TICKERS
from investorbot.integrations.simulation.interfaces import IDataProvider
from investorbot.structs.internal import LatestTrade


def get_first_row() -> dict:
    return {x["i"]: x["a"] for x in TICKERS}


class DataProvider(IDataProvider):
    time_series_data: DataFrame
    rng = np.random.default_rng(seed=2322)
    current_ticker_values: Tuple[dict, datetime] = {
        ticker["i"]: ticker["a"] for ticker in TICKERS
    }, datetime.now().timestamp() * 1000
    trend_percentage = 0.0
    start_time = datetime.now().timestamp() * 1000
    time_delta = 20 * 1000

    def __init__(self):
        if path.exists(TIME_SERIES_DATA_PATH):
            self.time_series_data = pd.read_csv(TIME_SERIES_DATA_PATH)

    def roll_dice(self) -> float:
        result = self.rng.integers(low=1, high=6, endpoint=True, size=4).mean()

        print(result)

        return result

    def trend_updater(self):
        trend_percentage = self.trend_percentage
        dice_roll = self.roll_dice()

        if dice_roll > 4.5:
            print("INCREASE")
            if trend_percentage < 0.0:
                trend_percentage = 0.0

            self.trend_percentage += 0.0002
        elif dice_roll < 2.5:
            print("DECREASE")
            if trend_percentage > 0.0:
                trend_percentage = 0

            self.trend_percentage -= 0.0002
        else:
            print("ON_TREND")

    def get_random_value(self, mean, st_deviation):
        return np.random.normal(loc=mean, scale=st_deviation)

    def increment_ts_data(self) -> Tuple[dict, datetime]:
        current_ticker_values = self.current_ticker_values[0]
        trend_percentage = self.trend_percentage
        start_time = self.start_time
        self.time_delta += 20 * 1000

        current_time = start_time + self.time_delta
        sigma = 0.01  # standard deviation

        for coin_name in current_ticker_values.keys():
            s = self.get_random_value(trend_percentage, sigma)

            new_price = float(current_ticker_values[coin_name]) * (1 + s)
            current_ticker_values[coin_name] = new_price

        self.current_ticker_values = current_ticker_values, current_time
        return self.current_ticker_values

    def generate_time_series_data(self):

        i = 0
        max_iter = 2880

        initial_data = get_first_row()
        time_series_data = pd.DataFrame(initial_data, index=[self.start_time])
        time_series_data.index.name = "t"

        print(time_series_data)

        while i < max_iter:
            new_values = self.increment_ts_data()
            df = pd.DataFrame(new_values[0], index=[new_values[1]])
            df.index.name = "t"
            time_series_data = pd.concat([time_series_data, df])

            if i % 100 == 0:
                self.trend_updater()
            i += 1

        time_series_data.to_csv(TIME_SERIES_DATA_PATH)
        self.time_series_data = time_series_data

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

        coin_data = self.time_series_data[["t", coin_name]]
        coin_data = [
            {"t": x, "v": y} for x, y in zip(coin_data["t"], coin_data[coin_name])
        ]

        return coin_data

    def run_in_real_time(self):
        i = 0

        while i < 300:
            self.increment_ts_data()

            print(self.current_ticker_values[1])
            time.sleep(1)
            i += 1
