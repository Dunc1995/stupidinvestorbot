from datetime import datetime
import math
from typing import List
import uuid

import sqlalchemy
from sqlalchemy import func
from investorbot import env
from investorbot.constants import INVESTMENT_INCREMENTS
from investorbot.enums import OrderStatus

# region coupling to cryptodotcom integration - ideally want complete decoupling but for the purposes
# of simulating the market this isn't such an issue.
from investorbot.integrations.cryptodotcom import mappings
from investorbot.integrations.simulation.data.instruments import INSTRUMENTS
from investorbot.integrations.cryptodotcom.structs import InstrumentJson

# endregion
from investorbot.integrations.simulation.interfaces import IDataProvider
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


class SimulationDbService(BaseAppService):

    def __init__(self, connection_string):
        super().__init__(SimulationBase, connection_string)


class SimulatedCryptoService(ICryptoService):
    def __init__(
        self,
        simulation_db_service: SimulationDbService,
        data_provider: IDataProvider,
    ):
        """As a simulated trading platform, the simulated crypto service requires a data provider as
        a dependency. This constructor specifies the IDataProvider interface anticipating either a
        randomized data implementation, or an implementation that uses historical data to simulate
        market conditions."""
        self.data = data_provider
        self.simulation_db = simulation_db_service

    def __get_guid(self):
        return str(uuid.uuid4())

    def __to_instrument_name(self, coin_name: str):
        """This is a design flaw on my part conflating coin name with instrument name. It's not such
        an issue whilst trading with USD exclusively."""
        return coin_name + "_USD" if "_USD" not in coin_name else coin_name

    def get_market_value_per_coin(self, coin_name: str) -> float:
        instrument_name = self.__to_instrument_name(coin_name)

        return float(self.data.current_ticker_values[0][instrument_name])

    def set_market_value_per_coin(self, coin_name: str, fake_value: float) -> float:
        """Do not use during live simulation - use this only for testing."""
        instrument_name = self.__to_instrument_name(coin_name)

        self.data.current_ticker_values[0][instrument_name] = fake_value

    def get_market_value(self, coin_name: str, quantity: float) -> float:
        """Derives market value by per_coin_value * quantity. If USD quantity then market value is a
        one-to-one ratio with market value.
        """

        if coin_name == "USD":
            return quantity

        return self.get_market_value_per_coin(coin_name) * float(quantity)

    def get_total_cash_balance(self) -> float:
        position_balances: List[PositionBalanceSimulated] = []
        session = self.simulation_db.session
        query = session.query(
            PositionBalanceSimulated,
            func.max(PositionBalanceSimulated.creation_time),
        ).group_by(PositionBalanceSimulated.coin_name)

        for item in query:
            position_balances.append(item[0])

        return sum(
            self.get_market_value(c.coin_name, c.quantity) for c in position_balances
        )

    def __get_coin_balance(self, coin_name: str) -> PositionBalanceSimulated | None:
        session = self.simulation_db.session

        data = (
            session.query(
                PositionBalanceSimulated,
                func.max(PositionBalanceSimulated.creation_time),
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
            current_wallet_entry = PositionBalanceSimulated(coin_name, 0.0, 0.0)
            current_wallet_entry.creation_time = env.time.now()

        new_coin_quantity = None

        # TODO quantity variable is only used once in this method - probably not necessary
        # TODO "USD" functionality may need separating out here.
        quantity_adjustment = total_value if coin_name == "USD" else quantity

        if is_selling:
            new_coin_quantity = current_wallet_entry.quantity - quantity_adjustment
        else:
            new_coin_quantity = current_wallet_entry.quantity + quantity_adjustment

        new_wallet_entry = PositionBalanceSimulated(
            coin_name=coin_name,
            quantity=new_coin_quantity,
            reserved_quantity=0.0,
        )

        new_wallet_entry.creation_time = env.time.now()

        self.simulation_db.add_item(new_wallet_entry)

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
        final_coin_name = coin_name.split("_")[0] if "_USD" in coin_name else coin_name

        result = self.__get_coin_balance(final_coin_name)

        market_value = self.get_market_value(result.coin_name, result.quantity)

        return PositionBalance(
            coin_name=result.coin_name,
            market_value=market_value,
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
        return self.data.get_latest_trade(coin_name)

    def get_latest_trades(self) -> List[LatestTrade]:
        return self.data.get_latest_trades()

    def get_coin_time_series_data(self, coin_name: str, hours=24) -> dict:
        return self.data.get_coin_time_series_data(coin_name)

    def get_order_detail(self, order_id: str) -> OrderDetail:
        session = self.simulation_db.session

        query = sqlalchemy.select(OrderDetailSimulated).where(
            OrderDetailSimulated.order_id == order_id
        )
        data = session.scalar(query)

        time_created_ms: datetime = data.creation_time

        return OrderDetail(
            status=data.status,
            order_id=data.order_id,
            coin_name=data.coin_name,
            order_value=data.order_value,
            quantity=data.quantity,
            fee=data.fee,
            fee_currency=data.fee_currency,
            time_created_ms=int(time_created_ms.timestamp() * 1000),
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

        current_time = env.time.now()
        order_detail.creation_time = current_time

        self.simulation_db.add_item(order_detail)

        buy_order.creation_time = current_time

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

        current_time = env.time.now()
        order_detail.creation_time = current_time

        self.simulation_db.add_item(order_detail)

        sell_order = SellOrder(sell_order_id, buy_order_id)
        sell_order.creation_time = current_time

        return sell_order
