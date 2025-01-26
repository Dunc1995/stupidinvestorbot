import math
from typing import List
import uuid

import sqlalchemy
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
        session = self.session

        query = sqlalchemy.select(PositionBalanceSimulated).where(
            PositionBalanceSimulated.coin_name == coin_name
        )
        data = session.scalar(query)

        return PositionBalance(**data)

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

    def __init__(self, connection_string):
        super().__init__(SimulationBase, connection_string)
