import json
import time
from typing import List

import numpy as np
from marketsimulator import market_simulator_service
from marketsimulator.models import Instrument, Ticker, ValuationData
from marketsimulator.structs import ValuationDataInMemory
from marketsimulator.data.instruments import INSTRUMENTS
from marketsimulator.data.tickers import TICKERS

current_ticker_values: List[ValuationDataInMemory] = []


def init_db():
    market_simulator_service.run_migration()

    instruments = [Instrument(**instrument) for instrument in INSTRUMENTS]
    tickers = [Ticker(**ticker) for ticker in TICKERS]

    market_simulator_service.add_items(instruments)
    market_simulator_service.add_items(tickers)


def add_ts_data() -> str:
    global current_ticker_values
    current_time = round(time.time() * 1000)
    mu, sigma = 0.002, 0.01  # mean and standard deviation
    new_values: List[ValuationDataInMemory] = []

    if len(current_ticker_values) == 0:
        tickers: List[Ticker] = market_simulator_service.get_all_items(Ticker)

        current_ticker_values = [
            ValuationDataInMemory(ticker.i, current_time, ticker.a)
            for ticker in tickers
        ]

    for coin in current_ticker_values:
        s = np.random.normal(loc=mu, scale=sigma)

        new_price = float(coin.v) * (1 + s)
        new_values.append(
            ValuationDataInMemory(coin.instrument_name, current_time, new_price)
        )

    market_simulator_service.add_items(
        [ValuationData.from_memory(new_value) for new_value in new_values]
    )
    current_ticker_values = new_values


def update_tickers():
    global current_ticker_values

    market_simulator_service.update_tickers(current_ticker_values)
