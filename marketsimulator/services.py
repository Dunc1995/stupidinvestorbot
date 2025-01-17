import time
from typing import List
import numpy as np
import sqlalchemy
from sqlalchemy import Engine
from sqlalchemy.orm import Session, joinedload

from investorbot.interfaces.services import ICryptoService
from investorbot.models import BuyOrder, CoinProperties, SellOrder
from investorbot.structs.egress import CoinPurchase, CoinSale
from investorbot.structs.internal import LatestTrade, OrderDetail, PositionBalance
from marketsimulator.constants import MARKET_SIMULATOR_APP_DB_CONNECTION
from marketsimulator.models import Base, Instrument, Ticker, ValuationData
from marketsimulator.structs import ValuationDataInMemory


class SimulatedCryptoService(ICryptoService):
    def get_coin_balance(self, coin_name: str) -> PositionBalance | None:
        pass

    def get_usd_balance(self) -> float:
        pass

    def get_investable_coin_count(self) -> int:
        pass

    def get_latest_trade(self, coin_name: str) -> LatestTrade:
        pass

    def get_latest_trades(self) -> List[LatestTrade]:
        pass

    def get_coin_time_series_data(self, coin_name: str, hours=24) -> dict:
        pass

    def get_order_detail(self, order_id: str) -> OrderDetail:
        pass

    def get_coin_properties(self) -> List[CoinProperties]:
        pass

    def place_coin_buy_order(self, order_spec: CoinPurchase) -> BuyOrder:
        pass

    def place_coin_sell_order(
        self, buy_order_id: str, coin_sale: CoinSale
    ) -> SellOrder:
        pass


class MarketSimulatorService:
    __engine: Engine
    rng = np.random.default_rng(seed=2322)
    current_ticker_values: List[ValuationDataInMemory] = []
    trend_percentage = 0.0
    start_time = round(time.time() * 1000) - 86_400_000
    time_delta = 20_000

    def __init__(self, connection_string=MARKET_SIMULATOR_APP_DB_CONNECTION):
        self.__engine = sqlalchemy.create_engine(
            connection_string, pool_size=200, max_overflow=0
        )

    @property
    def session(self) -> Session:
        return Session(self.__engine)

    def run_migration(self):
        Base.metadata.create_all(self.__engine)

    def add_item(self, db_object: Base):
        with self.session as session:
            session.add(db_object)
            session.commit()

    def add_items(self, db_objects: List[Base]):
        with self.session as session:
            session.add_all(db_objects)
            session.commit()

    def get_all_items(self, type: Base) -> List[Base]:
        items_list = []
        session = self.session

        query = sqlalchemy.select(type)
        for item in session.scalars(query):
            items_list.append(item)

        return items_list

    def update_tickers(self):

        with self.session as session:
            query = sqlalchemy.select(Ticker)
            for ticker in session.scalars(query):

                current_params = next(
                    (
                        x
                        for x in self.current_ticker_values
                        if x.instrument_name == ticker.i
                    ),
                    None,
                )

                ticker.a = current_params.v
                ticker.t = current_params.t

            session.commit()

        print("Tickers Updated!")

    def get_valuation(self, coin_name: str) -> Instrument:
        session = self.session

        query = (
            sqlalchemy.select(Instrument)
            .where(Instrument.symbol == coin_name)
            .options(joinedload(Instrument.valuation))
        )

        return session.scalar(query)

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
        new_values: List[ValuationDataInMemory] = []

        if len(current_ticker_values) == 0:
            tickers: List[Ticker] = self.get_all_items(Ticker)

            current_ticker_values = [
                ValuationDataInMemory(ticker.i, current_time, ticker.a)
                for ticker in tickers
            ]

        for coin in current_ticker_values:
            s = self.get_random_value(trend_percentage, sigma)

            new_price = float(coin.v) * (1 + s)
            new_values.append(
                ValuationDataInMemory(coin.instrument_name, current_time, new_price)
            )

        self.add_items(
            [ValuationData.from_memory(new_value) for new_value in new_values]
        )
        self.current_ticker_values = new_values

    def add_enumerable_ts_data(self):
        for i in range(10):
            self.add_ts_data()
