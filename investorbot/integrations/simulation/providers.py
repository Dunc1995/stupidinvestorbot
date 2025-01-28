from datetime import time
from typing import List
import numpy as np

from investorbot.integrations.simulation.data.tickers import TICKERS
from investorbot.integrations.simulation.structs import ValuationData


class DataProvider:
    rng = np.random.default_rng(seed=2322)
    current_ticker_values: List[ValuationData] = []
    trend_percentage = 0.0
    start_time = round(time.time() * 1000) - 86_400_000
    time_delta = 20_000

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

            self.trend_percentage += 0.002
        elif dice_roll < 2.5:
            print("DECREASE")
            if trend_percentage > 0.0:
                trend_percentage = 0

            self.trend_percentage -= 0.002
        else:
            print("ON_TREND")

    def get_random_value(self, mean, st_deviation):
        return np.random.normal(loc=mean, scale=st_deviation)

    def add_ts_data(
        self,
    ):
        current_ticker_values = self.current_ticker_values
        trend_percentage = self.trend_percentage
        start_time = self.start_time
        self.time_delta += 20_000

        current_time = start_time + self.time_delta
        sigma = 0.01  # standard deviation
        new_values: List[ValuationData] = []

        if len(current_ticker_values) == 0:
            current_ticker_values = [
                ValuationData(ticker["i"], current_time, ticker["a"])
                for ticker in TICKERS
            ]

        for coin in current_ticker_values:
            s = self.get_random_value(trend_percentage, sigma)

            new_price = float(coin.v) * (1 + s)
            new_values.append(
                ValuationData(coin.instrument_name, current_time, new_price)
            )

        self.current_ticker_values = new_values
