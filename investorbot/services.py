import logging
import math
from typing import List

import sqlalchemy
from sqlalchemy import Engine
from sqlalchemy.orm import Session, joinedload

from investorbot.constants import (
    CRYPTO_KEY,
    CRYPTO_SECRET_KEY,
    DEFAULT_LOGS_NAME,
    INVESTMENT_INCREMENTS,
    INVESTOR_APP_DB_CONNECTION,
    MAX_COINS,
)
from investorbot.http.market import MarketHttpClient
from investorbot.http.user import UserHttpClient
from investorbot.structs.internal import (
    OrderDetail,
    LatestTrade,
    PositionBalance,
    RatingThreshold,
)
from investorbot.structs.egress import CoinPurchase, CoinSale
from investorbot.models import (
    Base,
    BuyOrder,
    CoinProperties,
    CoinSelectionCriteria,
    MarketAnalysis,
    SellOrder,
    TimeSeriesSummary,
)
from investorbot.timeseries import time_now

logger = logging.getLogger(DEFAULT_LOGS_NAME)


class CryptoService:
    market: MarketHttpClient
    user: UserHttpClient

    def __init__(self):
        self.market = MarketHttpClient()
        self.user = UserHttpClient(CRYPTO_KEY, CRYPTO_SECRET_KEY)

    def get_coin_balance(self, coin_name: str) -> PositionBalance | None:
        wallet_balance = self.user.get_balance()

        name = coin_name.split("_")[0] if "_USD" in coin_name else coin_name

        balance = next(
            (x for x in wallet_balance.position_balances if x.instrument_name == name),
            None,
        )

        return PositionBalance.from_json(balance) if balance is not None else balance

    def get_usd_balance(self) -> float:
        usd_balance = float(self.get_coin_balance("USD").market_value)

        logger.info(f"Your balance is ${usd_balance}")

        return usd_balance

    def get_investable_coin_count(self) -> int:
        user_balance = self.get_usd_balance()

        number_of_coins_to_invest = math.floor(user_balance / INVESTMENT_INCREMENTS)

        if number_of_coins_to_invest > MAX_COINS:
            number_of_coins_to_invest = MAX_COINS

        return number_of_coins_to_invest

    def get_latest_trade(self, coin_name: str) -> LatestTrade:
        ticker_json = self.market.get_ticker(coin_name)

        return LatestTrade(ticker_json)

    def get_latest_trades(self) -> List[LatestTrade]:
        tickers = self.market.get_usd_tickers()
        trades = [LatestTrade(ticker) for ticker in tickers]

        return trades

    # TODO write class for valuation data
    def get_coin_time_series_data(self, coin_name: str) -> dict:
        return self.market.get_valuation(coin_name, "mark_price")

    def get_order_detail(self, order_id: str) -> OrderDetail:
        order_detail_json = self.user.get_order_detail(order_id)

        return OrderDetail.from_json(order_detail_json)

    def get_coin_properties(self) -> List[CoinProperties]:
        instruments = self.market.get_instruments()

        return [
            CoinProperties.from_instrument_json(instrument)
            for instrument in instruments
        ]

    def place_coin_buy_order(self, order_spec: CoinPurchase) -> BuyOrder:

        order = self.user.create_order(
            order_spec.coin_properties.coin_name,
            order_spec.price_per_coin,
            order_spec.quantity,
            "BUY",
        )

        return BuyOrder(
            buy_order_id=order.client_oid,
            coin_name=order_spec.coin_properties.coin_name,
        )

    def place_coin_sell_order(
        self, buy_order_id: str, coin_sale: CoinSale
    ) -> SellOrder:
        order = self.user.create_order(
            coin_sale.coin_properties.coin_name,
            coin_sale.price_per_coin,
            coin_sale.quantity,
            "SELL",
        )

        sell_order = SellOrder(order.client_oid, buy_order_id)

        return sell_order


class AppService:
    __engine: Engine

    def __init__(self, connection_string=INVESTOR_APP_DB_CONNECTION):
        self.__engine = sqlalchemy.create_engine(connection_string)

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

    def get_buy_order(self, buy_order_id: str) -> BuyOrder | None:
        session = self.session

        query = (
            sqlalchemy.select(BuyOrder)
            .where(BuyOrder.buy_order_id == buy_order_id)
            .options(joinedload(BuyOrder.sell_order))
        )

        return session.scalar(query)

    def get_all_buy_orders(self) -> List[BuyOrder]:
        items_list = []
        session = self.session

        query = (
            sqlalchemy.select(BuyOrder)
            .options(joinedload(BuyOrder.coin_properties))
            .options(joinedload(BuyOrder.sell_order))
        )

        for item in session.scalars(query):
            items_list.append(item)

        return items_list

    def delete_buy_order(self, buy_order_id: int):
        with self.session as session:
            item = (
                session.query(BuyOrder)
                .where(BuyOrder.buy_order_id == buy_order_id)
                .first()
            )

            session.delete(item)
            session.commit()

    def get_time_series_with_coin_name(
        self, coin_name: str
    ) -> List[TimeSeriesSummary] | None:
        ts_data = []
        session = self.session

        query = sqlalchemy.select(TimeSeriesSummary).where(
            TimeSeriesSummary.coin_name == coin_name
        )
        for item in session.scalars(query):
            ts_data.append(item)

        return ts_data

    def get_market_analysis(self) -> MarketAnalysis | None:
        items_list = []
        session = self.session

        query = session.query(MarketAnalysis).options(
            joinedload(MarketAnalysis.ts_data).subqueryload(TimeSeriesSummary.modes)
        )

        for item in session.scalars(query):
            items_list.append(item)

        list_length = len(items_list)

        # TODO enable this to handle multiple market analysis entries
        if list_length > 1:
            raise NotImplementedError(
                "Investor bot can only handle one market analysis in its database currently."
            )

        return items_list[0] if list_length == 1 else None

    def delete_existing_time_series(self):
        with self.session as session:
            now = time_now()
            query = (
                session.query(MarketAnalysis)
                .options(
                    joinedload(MarketAnalysis.ts_data).subqueryload(
                        TimeSeriesSummary.modes
                    )
                )
                .where(MarketAnalysis.creation_time_ms < now)
            )

            for item in session.scalars(query):
                session.delete(item)

            session.commit()

    def get_coin_properties(self, coin_name: str) -> CoinProperties | None:
        session = self.session

        query = sqlalchemy.select(CoinProperties).where(
            CoinProperties.coin_name == coin_name
        )
        return session.scalar(query)

    def get_rating_thresholds(self) -> List[RatingThreshold]:
        coin_selection_criteria = self.get_all_items(CoinSelectionCriteria)

        return [
            RatingThreshold(
                rating_id=criteria.rating_id,
                rating_upper_unbounded=criteria.rating_upper_unbounded,
                rating_upper_threshold=criteria.rating_upper_threshold,
                rating_lower_unbounded=criteria.rating_lower_unbounded,
                rating_lower_threshold=criteria.rating_lower_threshold,
            )
            for criteria in coin_selection_criteria
        ]
