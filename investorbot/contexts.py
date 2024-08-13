import logging
import math
import time
from typing import List
from decimal import *

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
from investorbot.structs.ingress import (
    PositionBalanceJson,
)
from investorbot.http.market import MarketHttpClient
from investorbot.http.user import UserHttpClient
from investorbot.structs.internal import (
    BuyOrderSpecification,
    OrderDetail,
    SellOrder,
    LatestTrade,
)
from investorbot.models import Base, BuyOrder, CoinProperties, TimeSeriesSummary

logger = logging.getLogger(DEFAULT_LOGS_NAME)


class CryptoContext:
    market: MarketHttpClient
    user: UserHttpClient

    def __init__(self):
        self.market = MarketHttpClient()
        self.user = UserHttpClient(CRYPTO_KEY, CRYPTO_SECRET_KEY)

    def get_coin_balance(self, instrument_name: str) -> PositionBalanceJson:
        wallet_balance = self.user.get_balance()

        balance = next(
            x
            for x in wallet_balance.position_balances
            if x.instrument_name == instrument_name
        )

        return balance

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

        return OrderDetail(order_detail_json)

    def get_coin_properties(self) -> List[CoinProperties]:
        instruments = self.market.get_instruments()

        return [CoinProperties(instrument) for instrument in instruments]

    def place_coin_buy_order(self, order_spec: BuyOrderSpecification) -> BuyOrder:

        order = self.user.create_order(
            order_spec.coin_name,
            order_spec.price_per_coin_str,
            order_spec.quantity_str,
            "BUY",
        )

        return BuyOrder(buy_order_id=order.client_oid, coin_name=order_spec.coin_name)

    # TODO this can be simplified
    def place_coin_sell_order(self, sell_order: SellOrder):
        """Places order for the input coin, accounting for discrepancies in coin quantity
        following any fee deductions. For example if 1.8 of a particular coin has been
        purchased, Crypto.com will deduct a fee from the coin quantity resulting in you
        actually receiving 1.795 of said coin. This fee may not necessarily respect the
        quantity tick size of the coin - e.g. you may have 1.795 of the coin, but only
        1.79 of the coin is actually sellable, because the quantity tick size is 0.01.
        """
        instrument = self.get_instrument(
            sell_order.coin_name
        )  #! TODO find a better way to store instrument data.
        quantity_remainder = sell_order.sellable_quantity % float(
            instrument.qty_tick_size
        )

        adjusted_sell_quantity = (
            sell_order.sellable_quantity - quantity_remainder
        )  # remainder needs deducting because Crypto.com fees don't respect their own quantity tick size requirement.

        sellable_vs_absolute_quantity_ratio = (
            adjusted_sell_quantity / sell_order.sellable_quantity
        )  # used to adjust final sell price after negating the quantity remainder

        adjusted_sell_price = (
            sellable_vs_absolute_quantity_ratio * sell_order.current_market_value
        ) / (
            adjusted_sell_quantity
        )  # sell price adjusted after negating quantity remainder.

        # string formatting removes any trailing zeros or dodgy rounding.

        if sell_order.market_value_rounding > 0:
            adjusted_sell_price = round(
                adjusted_sell_price, sell_order.market_value_rounding
            )
            logger.info(
                f"Rounding sell value to {sell_order.market_value_rounding} decimal places."
            )

        adjusted_sell_quantity_string = f"{adjusted_sell_quantity:g}"
        adjusted_sell_price_string = f"{adjusted_sell_price:g}"

        self.user.create_order(
            sell_order.coin_name,
            adjusted_sell_price_string,
            adjusted_sell_quantity_string,
            "SELL",
        )


class AppContext:
    __engine: Engine

    def __init__(
        self,
        connection_string=INVESTOR_APP_DB_CONNECTION + "app.db",
    ):
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

        query = sqlalchemy.select(BuyOrder).where(BuyOrder.buy_order_id == buy_order_id)
        return session.scalar(query)

    def get_all_buy_orders(self) -> List[BuyOrder]:
        return self.get_all_items(BuyOrder)

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

    def get_all_time_series_summaries(self) -> List[TimeSeriesSummary]:
        return self.get_all_items(TimeSeriesSummary)

    def delete_existing_time_series(self):
        with self.session as session:
            time_now = int(time.time() * 1000)
            query = (
                session.query(TimeSeriesSummary)
                .options(joinedload(TimeSeriesSummary.modes))
                .where(TimeSeriesSummary.creation_time_ms < time_now)
            )

            for item in session.scalars(query):
                session.delete(item)

            session.commit()
