from typing import Any, Generator, List
from decimal import *
import logging

import sqlalchemy
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from investorbot.constants import (
    CRYPTO_KEY,
    CRYPTO_SECRET_KEY,
    INVESTOR_APP_DB_CONNECTION,
)
from investorbot.structs.ingress import (
    PositionBalanceJson,
)
from investorbot.http.market import MarketHttpClient
from investorbot.http.user import UserHttpClient
from investorbot.structs.internal import OrderDetail, SellOrder
from investorbot.models import Base, BuyOrder, TimeSeriesSummary

# from chalicelib.models.crypto import PositionBalance, UserBalance

logger = logging.getLogger("client")


class CryptoContext:
    market: MarketHttpClient
    user: UserHttpClient

    def __init__(self):
        self.market = MarketHttpClient()
        self.user = UserHttpClient(CRYPTO_KEY, CRYPTO_SECRET_KEY)

    # @staticmethod
    # def __should_select_coin(summary: TimeSeriesSummary, strategy: str) -> bool:
    #     select_coin = False

    #     match strategy:
    #         case CoinSelectionStrategies.HIGH_GAIN:
    #             select_coin = CoinSelectionStrategies.high_gain(summary)
    #         case CoinSelectionStrategies.CONSERVATIVE:
    #             select_coin = CoinSelectionStrategies.conservative(summary)
    #         case CoinSelectionStrategies.ALL_GUNS_BLAZING:
    #             select_coin = CoinSelectionStrategies.all_guns_blazing(summary)
    #         case _:
    #             select_coin = False

    #     return select_coin

    def get_coin_time_series_data(self, coin_name: str) -> dict:
        return self.market.get_valuation(coin_name, "mark_price")

    def get_order_detail(self, order_id: str) -> OrderDetail:
        order_detail_json = self.user.get_order_detail(order_id)

        return OrderDetail(order_detail_json)

    def get_coin_balance(self, instrument_name: str) -> PositionBalanceJson:
        wallet_balance = self.user.get_balance()

        balance = next(
            x
            for x in wallet_balance.position_balances
            if x.instrument_name == instrument_name
        )

        return balance

    def get_usd_balance(self) -> float:
        usd_balance = self.get_coin_balance("USD").market_value

        return usd_balance

    def place_coin_buy_orders(
        self, coin_summaries: List[TimeSeriesSummary]
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


class AppContext:
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
