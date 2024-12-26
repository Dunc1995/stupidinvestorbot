import json
import time
from typing import List

import numpy as np
from marketsimulator import market_simulator_service
from marketsimulator.models import Instrument, ValuationData
from marketsimulator.instruments import INSTRUMENTS


def init_db():
    market_simulator_service.run_migration()

    instruments = [Instrument(**instrument) for instrument in INSTRUMENTS]

    market_simulator_service.add_items(instruments)


def add_ts_data() -> str:
    instrument = "BTC_USD"
    current_value = 5

    current_time = round(time.time() * 1000)

    mu, sigma = 0.002, 0.01  # mean and standard deviation
    s = np.random.normal(loc=mu, scale=sigma)

    new_value = current_value * (1 + s)

    market_simulator_service.add_item(
        ValuationData(instrument, current_time, new_value)
    )
    print(new_value)
