import datetime as dt
import json
from typing import Any, Generator, List
import pandas as pd
from decimal import *
import logging

import sqlalchemy
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from investorbot.constants import (
    INVESTMENT_INCREMENTS,
    CRYPTO_KEY,
    CRYPTO_SECRET_KEY,
    INVESTOR_APP_DB_CONNECTION,
)
from investorbot.structs.ingress import (
    InstrumentJson,
    OrderDetailJson,
    OrderJson,
    PositionBalanceJson,
)
from investorbot.strategies import CoinSelectionStrategies
from investorbot.http.market import MarketHttpClient
from investorbot.http.user import UserHttpClient
from investorbot.structs.ingress import TickerJson
from investorbot.structs.internal import CoinSummary, SellOrder
from investorbot.models import Base, BuyOrder

# from chalicelib.models.crypto import PositionBalance, UserBalance

logger = logging.getLogger("client")


class CryptoRepo:
    market: MarketHttpClient
    user: UserHttpClient

    def __init__(self):
        self.market = MarketHttpClient()
        self.user = UserHttpClient(CRYPTO_KEY, CRYPTO_SECRET_KEY)
        self.__instruments = None

    @property
    def instruments(self):
        if self.__instruments is None:
            self.__instruments = self.market.get_instruments()

        return self.__instruments

    def get_instrument(self, instrument_name) -> InstrumentJson:
        return next(x for x in self.instruments if x.symbol == instrument_name)

    @staticmethod
    def __should_select_coin(summary: CoinSummary, strategy: str) -> bool:
        select_coin = False

        match strategy:
            case CoinSelectionStrategies.HIGH_GAIN:
                select_coin = CoinSelectionStrategies.high_gain(summary)
            case CoinSelectionStrategies.CONSERVATIVE:
                select_coin = CoinSelectionStrategies.conservative(summary)
            case CoinSelectionStrategies.ALL_GUNS_BLAZING:
                select_coin = CoinSelectionStrategies.all_guns_blazing(summary)
            case _:
                select_coin = False

        return select_coin

    def __get_coin_summary(self, coin: TickerJson) -> CoinSummary:
        """Fetches time-series data for the coin of interest and summarizes basic statistical properties via
        the CoinSummary object. Used for determining which coins to invest in.

        Args:
            coin (Ticker): Object obtained via API call to Crypto.com API.

        Returns:
            CoinSummary: data container for coin statistics.
        """
        time_series_data = self.market.get_valuation(coin.instrument_name, "mark_price")

        df = pd.DataFrame.from_dict(time_series_data)
        df["t"] = df["t"].apply(lambda x: dt.datetime.fromtimestamp(x / 1000))
        df["v"] = df["v"].astype(float)

        stats = df
        mean = stats["v"].mean()
        std = stats["v"].std()
        modes = stats["v"].mode()
        percentage_std = float(std) / float(mean)
        quantity_tick_size = self.get_instrument(coin.instrument_name).qty_tick_size

        coin_summary = CoinSummary(
            name=coin.instrument_name,
            latest_trade=float(coin.latest_trade),
            quantity_tick_size=float(quantity_tick_size),
            mean_24h=mean,
            modes_24h=modes,
            std_24h=std,
            percentage_std_24h=percentage_std,
            percentage_change_24h=float(coin.percentage_change_24h),
            is_greater_than_mean=bool(float(coin.latest_trade) - mean > 0),
            is_greater_than_std=bool(float(coin.latest_trade) - (mean + std) > 0),
        )

        coin_summary.coin_quantity = INVESTMENT_INCREMENTS

        return coin_summary

    def get_order_detail(self, order_id: str):
        order_detail_json = self.user.get_order_detail(order_id)

        return order_detail_json.translate()

    def get_coin_balance(self, instrument_name: str) -> PositionBalanceJson:
        wallet_balance = self.user.get_balance()

        balance = next(
            x
            for x in wallet_balance.position_balances
            if x.instrument_name == instrument_name
        )

        return balance

    def get_usd_balance(self):
        usd_balance = self.get_coin_balance("USD").market_value

        return usd_balance

    def select_coins_of_interest(
        self, strategy: str, number_of_coins: int
    ) -> List[CoinSummary] | None:
        coin_summaries = []

        for coin in self.market.get_usd_coins():
            logger.debug(f"Fetching latest 24hr dataset for {coin.instrument_name}.")

            summary = self.__get_coin_summary(coin)

            if self.__should_select_coin(summary, strategy):
                logger.debug(f"Selecting the following coin: {summary}")
                coin_summaries.append(summary)
            else:
                logger.debug(f"Rejecting the following: {summary}")

        if number_of_coins < len(coin_summaries):
            selected_coins = coin_summaries[:number_of_coins]
            coin_summaries = selected_coins

        return coin_summaries

    def place_coin_buy_orders(
        self, coin_summaries: List[CoinSummary]
    ) -> Generator[BuyOrder, Any, None]:

        for coin in coin_summaries:
            # string formatting removes any trailing zeros or dodgy rounding.
            coin_quantity_string = f"{coin.coin_quantity:g}"
            latest_trade_string = f"{coin.latest_trade:g}"

            order = self.user.create_order(
                coin.name, latest_trade_string, coin_quantity_string, "BUY"
            )

            yield BuyOrder(buy_order_id=order.client_oid, coin_name=coin.name)

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


class InvestorBotRepo:
    __engine: Engine

    def __init__(
        self,
        connection_string=INVESTOR_APP_DB_CONNECTION + "app.db",
    ):
        self.__engine = sqlalchemy.create_engine(connection_string)

    def add_item(self, db_object: Base):
        with Session(self.__engine) as session:
            session.add(db_object)
            session.commit()

    def add_items(self, db_objects: List[Base]):
        with Session(self.__engine) as session:
            session.add_all(db_objects)
            session.commit()

    def get_buy_order(self, buy_order_id: str) -> BuyOrder | None:
        session = Session(self.__engine)

        query = sqlalchemy.select(BuyOrder).where(BuyOrder.buy_order_id == buy_order_id)
        return session.scalar(query)

    def get_all_buy_orders(self) -> List[BuyOrder]:
        buy_orders: List[BuyOrder] = []
        session = Session(self.__engine)

        query = sqlalchemy.select(BuyOrder)
        for buy_order in session.scalars(query):
            buy_orders.append(buy_order)

    def run_migration(self):
        Base.metadata.create_all(self.__engine)
