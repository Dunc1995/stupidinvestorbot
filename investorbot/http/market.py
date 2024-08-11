import logging
from typing import List
from investorbot.constants import CRYPTO_MARKET_URL
from investorbot.http.base import HttpClient
from investorbot.models.app import Ticker
from investorbot.models.crypto import Instrument

logger = logging.getLogger("client")


class MarketHttpClient(HttpClient):
    def __init__(
        self,
        api_url=CRYPTO_MARKET_URL,
    ):
        super().__init__(api_url=api_url, id_incr=1)

    def get_usd_coins(self) -> list[Ticker]:
        ticker_data = self.get_data("get-tickers")

        data = [
            Ticker(obj)
            for obj in ticker_data
            if str(obj["i"]).endswith("_USD") and float(obj["vv"]) > 200_000.0
        ]

        result = sorted(
            data, key=lambda x: tuple(x.percentage_change_24h)
        )  # TODO write test for sorting behaviour - this is pretty implicit
        result.reverse()

        return result

    def get_instruments(self) -> List[Instrument]:
        instrument_data = self.get_data("get-instruments")

        data = [Instrument(**obj) for obj in instrument_data]

        return data

    def get_ticker(self, instrument_name: str) -> Ticker:
        ticker_data = self.get_data(f"get-tickers?instrument_name={instrument_name}")

        data = [Ticker(obj) for obj in ticker_data]

        return data[0]

    def get_valuation(self, instrument_name: str, valuation_type: str) -> dict:
        # ! start/end time query parameters don't seem to work hence the following being commented out
        # to_unix = lambda x: int(time.mktime(x.timetuple()) * 1000)

        # date_now = to_unix(dt.datetime.now())
        # date_past = to_unix(dt.datetime.now() - dt.timedelta(days=1))

        # * count query max ~4000 data points going back 24h
        # TODO attempt to retrieve data >24h ago.
        valuation_data = self.get_data(
            f"get-valuations?instrument_name={instrument_name}&valuation_type={valuation_type}&count=4000"
        )

        return valuation_data
