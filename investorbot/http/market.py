from typing import List
from investorbot.constants import CRYPTO_MARKET_URL
from investorbot.http.base import HttpClient
from investorbot.structs.ingress import InstrumentJson, TickerJson


class MarketHttpClient(HttpClient):
    def __init__(
        self,
        api_url=CRYPTO_MARKET_URL,
    ):
        super().__init__(api_url=api_url, id_incr=1)

    def get_usd_tickers(self) -> list[TickerJson]:
        ticker_data = self.get_data("get-tickers")

        data = [
            TickerJson(obj)
            for obj in ticker_data
            if str(obj["i"]).endswith("_USD")
            and not str(obj["i"]).startswith("USDT_")
            and float(obj["vv"]) > 200_000.0
        ]

        result = sorted(
            data,
            key=lambda x: float(x.percentage_change_24h)
            * float(x.total_traded_volume_usd_24h),
        )  # TODO write test for sorting behavior - this is pretty implicit
        result.reverse()

        return result

    def get_instruments(self) -> List[InstrumentJson]:
        instrument_data = self.get_data("get-instruments")

        data = [InstrumentJson(**obj) for obj in instrument_data]

        return data

    def get_ticker(self, instrument_name: str) -> TickerJson:
        ticker_data = self.get_data(f"get-tickers?instrument_name={instrument_name}")

        data = [TickerJson(obj) for obj in ticker_data]

        return data[0]

    def __hours_to_count(self, hours: int | float):
        return int((2880 / 24) * hours)

    def get_valuation(
        self, instrument_name: str, valuation_type: str, hours=24
    ) -> dict:
        """Allegedly fetches per minute data market valuation data for the requested coin name
        (https://exchange-docs.crypto.com/exchange/v1/rest-ws/index.html#public-get-valuations). If
        the documentation was correct you'd need to request 1440 data points (24 hours * 60
        minutes), but in reality, the API returns alternating intervals of 20 seconds and 40
        seconds, hence the default count here is 2880 to correspond with 24 hours-worth of data.
        """
        count = self.__hours_to_count(hours)

        valuation_data = self.get_data(
            f"get-valuations?instrument_name={instrument_name}&valuation_type={valuation_type}&count={count}"
        )

        return valuation_data
