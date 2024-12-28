import json
import time
from typing import List

import numpy as np
from marketsimulator import market_simulator_service
from marketsimulator.models import Instrument, Ticker, ValuationData
from marketsimulator.structs import ValuationDataInMemory
from marketsimulator.data.instruments import INSTRUMENTS
from marketsimulator.data.tickers import TICKERS


def init_db():
    market_simulator_service.run_migration()

    instruments = [Instrument(**instrument) for instrument in INSTRUMENTS]
    tickers = [Ticker(**ticker) for ticker in TICKERS]

    market_simulator_service.add_items(instruments)
    market_simulator_service.add_items(tickers)
