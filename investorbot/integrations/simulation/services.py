import math
from typing import List
import uuid

import sqlalchemy
from sqlalchemy import func
from investorbot.constants import INVESTMENT_INCREMENTS
from investorbot.enums import OrderStatus

# region coupling to cryptodotcom integration - ideally want complete decoupling but for the purposes
# of simulating the market this isn't such an issue.
from investorbot.integrations.cryptodotcom import mappings
from investorbot.integrations.cryptodotcom.constants import INSTRUMENTS
from investorbot.integrations.cryptodotcom.structs import InstrumentJson

# endregion
from investorbot.interfaces.services import ICryptoService
from investorbot.models import BuyOrder, CoinProperties, SellOrder
from investorbot.services import BaseAppService
from investorbot.integrations.simulation.models import (
    SimulationBase,
    OrderDetailSimulated,
    PositionBalanceSimulated,
)
from investorbot.structs.egress import CoinPurchase, CoinSale
from investorbot.structs.internal import LatestTrade, OrderDetail, PositionBalance


class SimulatedCryptoService(ICryptoService):
    def __init__(self, simulation_service: "SimulationService"):
        self.simulation_service = simulation_service

    def __get_guid(self):
        return str(uuid.uuid4())

    def __get_total_cash_balance(self) -> float:
        position_balances: List[PositionBalanceSimulated] = []
        session = self.session
        query = sqlalchemy.select(PositionBalanceSimulated)

        for item in session.scalars(query):
            position_balances.append(item)

        return sum(c.market_value for c in position_balances)

    def get_coin_balance(self, coin_name: str) -> PositionBalance | None:
        session = self.simulation_service.session

        data = (
            session.query(
                PositionBalanceSimulated,
                func.max(PositionBalanceSimulated.time_creates_ms),
            )
            .filter(PositionBalanceSimulated.coin_name == coin_name)
            .first()
        )

        result: PositionBalanceSimulated = data[0]

        return PositionBalance(
            coin_name=result.coin_name,
            market_value=result.market_value,
            quantity=result.quantity,
            reserved_quantity=result.reserved_quantity,
        )

    def get_usd_balance(self) -> float:
        usd_balance = float(self.get_coin_balance("USD").market_value)

        return usd_balance

    def get_investable_coin_count(self) -> int:
        user_balance = self.get_usd_balance()

        percentage_to_invest = (
            user_balance / self.__get_total_cash_balance() - 0.5
        )  # TODO make configurable

        number_of_coins_to_invest = (
            math.floor(user_balance * percentage_to_invest / INVESTMENT_INCREMENTS)
            if percentage_to_invest > 0
            else 0
        )

        return number_of_coins_to_invest

    def get_latest_trade(self, coin_name: str) -> LatestTrade:
        # TODO maybe fetch from memory
        pass

    def get_latest_trades(self) -> List[LatestTrade]:
        # TODO maybe fetch from memory
        pass

    def get_coin_time_series_data(self, coin_name: str, hours=24) -> dict:
        # TODO maybe fetch from memory
        pass

    def get_order_detail(self, order_id: str) -> OrderDetail:
        session = self.session

        query = sqlalchemy.select(OrderDetailSimulated).where(
            OrderDetailSimulated.order_id == order_id
        )
        data = session.scalar(query)

        return OrderDetail(**data)

    def get_coin_properties(self) -> List[CoinProperties]:
        coin_properties = [
            mappings.json_to_coin_properties(InstrumentJson(**coin_properties))
            for coin_properties in INSTRUMENTS
        ]

        return coin_properties

    def place_coin_buy_order(self, order_spec: CoinPurchase) -> BuyOrder:
        order_id = self.__get_guid()

        buy_order = BuyOrder(
            order_id,
            order_spec.coin_properties.coin_name,
            order_spec.price_per_coin,
        )

        total_value: float = order_spec.price_per_coin * order_spec.quantity

        order_detail = OrderDetailSimulated(
            OrderStatus.COMPLETED.value,
            order_id,
            buy_order.coin_name,
            total_value,
            order_spec.quantity,
            order_spec.quantity,
            total_value,
            0.005 * total_value,
            buy_order.coin_name.split("_")[0],
        )

        self.simulation_service.add_item(order_detail)

        return buy_order

    def place_coin_sell_order(
        self, buy_order_id: str, coin_sale: CoinSale
    ) -> SellOrder:
        sell_order_id = self.__get_guid()
        total_value = coin_sale.price_per_coin * coin_sale.quantity

        order_detail = OrderDetailSimulated(
            OrderStatus.COMPLETED.value,
            sell_order_id,
            coin_sale.coin_name,
            total_value,
            coin_sale.quantity,
            coin_sale.quantity,
            total_value,
            0.005 * total_value,
            coin_sale.coin_name.split("_")[0],
        )

        self.simulation_service.add_item(order_detail)

        sell_order = SellOrder(sell_order_id, buy_order_id)

        return sell_order


class SimulationService(BaseAppService):
    # rng = np.random.default_rng(seed=2322)
    # current_ticker_values: List[ValuationDataInMemory] = []
    # trend_percentage = 0.0
    # start_time = round(time.time() * 1000) - 86_400_000
    # time_delta = 20_000

    def __init__(self, connection_string):
        super().__init__(SimulationBase, connection_string)

    # def roll_dice(self) -> float:
    #     result = self.rng.integers(low=1, high=6, endpoint=True, size=4).mean()

    #     print(result)

    #     return result

    # def trend_updater(self):
    #     trend_percentage = self.trend_percentage
    #     dice_roll = self.roll_dice()

    #     if dice_roll > 4.5:
    #         print("INCREASE")
    #         if trend_percentage < 0.0:
    #             trend_percentage = 0.0

    #         self.trend_percentage += 0.002
    #     elif dice_roll < 2.5:
    #         print("DECREASE")
    #         if trend_percentage > 0.0:
    #             trend_percentage = 0

    #         self.trend_percentage -= 0.002
    #     else:
    #         print("ON_TREND")

    # def get_random_value(self, mean, st_deviation):
    #     return np.random.normal(loc=mean, scale=st_deviation)

    # def add_ts_data(
    #     self,
    # ):
    #     current_ticker_values = self.current_ticker_values
    #     trend_percentage = self.trend_percentage
    #     start_time = self.start_time
    #     self.time_delta += 20_000

    #     current_time = start_time + self.time_delta
    #     sigma = 0.01  # standard deviation
    #     new_values: List[ValuationDataInMemory] = []

    #     if len(current_ticker_values) == 0:
    #         tickers: List[Ticker] = self.get_all_items(Ticker)

    #         current_ticker_values = [
    #             ValuationDataInMemory(ticker.i, current_time, ticker.a)
    #             for ticker in tickers
    #         ]

    #     for coin in current_ticker_values:
    #         s = self.get_random_value(trend_percentage, sigma)

    #         new_price = float(coin.v) * (1 + s)
    #         new_values.append(
    #             ValuationDataInMemory(coin.instrument_name, current_time, new_price)
    #         )

    #     self.add_items(
    #         [ValuationData.from_memory(new_value) for new_value in new_values]
    #     )
    #     self.current_ticker_values = new_values
