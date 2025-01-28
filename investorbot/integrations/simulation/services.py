from datetime import datetime, timedelta
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
from investorbot.integrations.simulation.data.instruments import INSTRUMENTS
from investorbot.integrations.cryptodotcom.structs import InstrumentJson

# endregion
from investorbot.integrations.simulation.interfaces import ITime
from investorbot.integrations.simulation.structs import PositionBalanceAdjustmentResult
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


class SimulationService(BaseAppService):

    def __init__(self, connection_string):
        super().__init__(SimulationBase, connection_string)


class TestingTime(ITime):
    __current_time: datetime

    def __init__(self):
        self.__current_time = datetime.now()

    def now(self) -> datetime:
        """Here I'm simulating the passage of time in a very crude sense. This is to be used
        whenever the point in time is mostly irrelevant or in simplistic tests."""
        self.__current_time += timedelta(minutes=1)

        return self.__current_time


class SimulatedCryptoService(ICryptoService):
    def __init__(self, simulation_service: SimulationService, time_service: ITime):
        self.simulation_service = simulation_service
        self.time_service = time_service

    def __get_guid(self):
        return str(uuid.uuid4())

    def get_total_cash_balance(self) -> float:
        position_balances: List[PositionBalanceSimulated] = []
        session = self.simulation_service.session
        query = session.query(
            PositionBalanceSimulated,
            func.max(PositionBalanceSimulated.time_creates_ms),
        ).group_by(PositionBalanceSimulated.coin_name)

        for item in query:
            position_balances.append(item[0])

        return sum(c.market_value for c in position_balances)

    def __get_coin_balance(self, coin_name: str) -> PositionBalanceSimulated | None:
        session = self.simulation_service.session

        data = (
            session.query(
                PositionBalanceSimulated,
                func.max(PositionBalanceSimulated.time_creates_ms),
            )
            .filter(PositionBalanceSimulated.coin_name == coin_name)
            .first()
        )

        return data[0]

    # TODO method can most likely be simplified.
    def __adjust_balance(
        self,
        coin_name: str,
        quantity: float,
        total_value: float,
        is_selling: bool,
    ):
        quantity = float(quantity)

        current_wallet_entry = self.__get_coin_balance(coin_name)

        if current_wallet_entry is None:
            current_wallet_entry = PositionBalanceSimulated(coin_name, 0.0, 0.0, 0.0)
            current_wallet_entry.time_creates_ms = self.time_service.now()

        new_coin_quantity = None
        new_coin_market_value = None

        # TODO quantity variable is only used once in this method - probably not necessary
        # TODO "USD" functionality may need separating out here.
        quantity_adjustment = total_value if coin_name == "USD" else quantity

        if is_selling:
            new_coin_quantity = current_wallet_entry.quantity - quantity_adjustment
            new_coin_market_value = current_wallet_entry.market_value - total_value
        else:
            new_coin_quantity = current_wallet_entry.quantity + quantity_adjustment
            new_coin_market_value = current_wallet_entry.market_value + total_value

        new_wallet_entry = PositionBalanceSimulated(
            coin_name=coin_name,
            market_value=new_coin_market_value,
            quantity=new_coin_quantity,
            reserved_quantity=0.0,
        )

        new_wallet_entry.time_creates_ms = self.time_service.now()

        self.simulation_service.add_item(new_wallet_entry)

    def __get_position_balance_adjustment(
        self, coin_name, quantity_str, price_per_coin_str, fee_pct=0.005
    ):
        quantity = float(quantity_str)
        price_per_coin = float(price_per_coin_str)

        total_value: float = float(price_per_coin) * quantity

        net_quantity = (1 - fee_pct) * quantity
        net_total_value = (1 - fee_pct) * total_value

        fee_amount = fee_pct * quantity
        fee_currency = coin_name.split("_")[0]

        return PositionBalanceAdjustmentResult(
            total_value,
            quantity,
            net_total_value,
            net_quantity,
            fee_amount,
            fee_currency,
        )

    def get_coin_balance(self, coin_name: str) -> PositionBalance | None:
        result = self.__get_coin_balance(coin_name)

        return PositionBalance(
            coin_name=result.coin_name,
            market_value=result.market_value,
            quantity=result.quantity,
            reserved_quantity=result.reserved_quantity,
        )

    def get_usd_balance(self) -> float:
        # ! Note here reserved quantity in realistic circumstances may confuse things whilst
        # ! trading in reality. For simulation purposes it's being ignored to simplify things.
        usd_balance = float(self.get_coin_balance("USD").market_value)

        return usd_balance

    def get_investable_coin_count(self) -> int:
        # TODO update tests once percentage-to-invest is configurable
        user_balance = self.get_usd_balance()
        total_cash_balance = self.get_total_cash_balance()

        percentage_to_invest = (
            user_balance / total_cash_balance - 0.5
        )  # TODO make configurable

        # FIXME INVESTMENT_INCREMENTS will break tests if changed.
        number_of_coins_to_invest = (
            math.floor(
                total_cash_balance * percentage_to_invest / INVESTMENT_INCREMENTS
            )
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
        session = self.simulation_service.session

        query = sqlalchemy.select(OrderDetailSimulated).where(
            OrderDetailSimulated.order_id == order_id
        )
        data = session.scalar(query)

        return OrderDetail(
            status=data.status,
            order_id=data.order_id,
            coin_name=data.coin_name,
            order_value=data.order_value,
            quantity=data.quantity,
            fee=data.fee,
            fee_currency=data.fee_currency,
            time_created_ms=data.time_creates_ms,
        )

    def get_coin_properties(self) -> List[CoinProperties]:
        coin_properties = [
            mappings.json_to_coin_properties(InstrumentJson(**coin_properties))
            for coin_properties in INSTRUMENTS
        ]

        return coin_properties

    def place_coin_buy_order(self, order_spec: CoinPurchase) -> BuyOrder:
        order_id = self.__get_guid()
        coin_name = order_spec.coin_properties.coin_name

        buy_order = BuyOrder(
            order_id,
            coin_name,
            order_spec.price_per_coin,
        )

        result = self.__get_position_balance_adjustment(
            coin_name, order_spec.quantity, order_spec.price_per_coin
        )

        quantity = result.quantity
        total_value = result.total_value
        net_quantity = result.net_quantity
        net_total_value = result.net_value
        fee_currency = result.fee_currency
        fee_amount = result.fee_amount

        self.__adjust_balance("USD", quantity, total_value, True)
        self.__adjust_balance(fee_currency, net_quantity, net_total_value, False)

        order_detail = OrderDetailSimulated(
            status=OrderStatus.COMPLETED.value,
            order_id=order_id,
            coin_name=coin_name,
            order_value=total_value,
            quantity=quantity,
            fee=fee_amount,
            fee_currency=fee_currency,
        )

        self.simulation_service.add_item(order_detail)

        return buy_order

    def place_coin_sell_order(
        self, buy_order_id: str, coin_sale: CoinSale
    ) -> SellOrder:
        sell_order_id = self.__get_guid()

        coin_name = coin_sale.coin_properties.coin_name

        result = self.__get_position_balance_adjustment(
            coin_name, coin_sale.quantity, coin_sale.price_per_coin
        )

        quantity = result.quantity
        total_value = result.total_value
        net_quantity = result.net_quantity
        net_total_value = result.net_value
        fee_currency = result.fee_currency
        fee_amount = result.fee_amount

        self.__adjust_balance("USD", quantity, net_total_value, False)
        self.__adjust_balance(fee_currency, net_quantity, net_total_value, True)

        order_detail = OrderDetailSimulated(
            status=OrderStatus.COMPLETED.value,
            order_id=sell_order_id,
            coin_name=coin_name,
            order_value=total_value,
            quantity=quantity,
            fee=fee_amount,
            fee_currency=fee_currency,
        )

        self.simulation_service.add_item(order_detail)

        sell_order = SellOrder(sell_order_id, buy_order_id)

        return sell_order
