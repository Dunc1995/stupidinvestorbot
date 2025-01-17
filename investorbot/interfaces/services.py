from abc import ABC, abstractmethod
from typing import List

from investorbot.models import BuyOrder, CoinProperties, SellOrder
from investorbot.structs.egress import CoinPurchase, CoinSale
from investorbot.structs.internal import LatestTrade, OrderDetail, PositionBalance


class ICryptoService(ABC):

    @abstractmethod
    def get_coin_balance(self, coin_name: str) -> PositionBalance | None:
        pass

    @abstractmethod
    def get_usd_balance(self) -> float:
        pass

    @abstractmethod
    def get_investable_coin_count(self) -> int:
        pass

    @abstractmethod
    def get_latest_trade(self, coin_name: str) -> LatestTrade:
        pass

    @abstractmethod
    def get_latest_trades(self) -> List[LatestTrade]:
        pass

    @abstractmethod
    def get_coin_time_series_data(self, coin_name: str, hours=24) -> dict:
        pass

    @abstractmethod
    def get_order_detail(self, order_id: str) -> OrderDetail:
        pass

    @abstractmethod
    def get_coin_properties(self) -> List[CoinProperties]:
        pass

    @abstractmethod
    def place_coin_buy_order(self, order_spec: CoinPurchase) -> BuyOrder:
        pass

    @abstractmethod
    def place_coin_sell_order(
        self, buy_order_id: str, coin_sale: CoinSale
    ) -> SellOrder:
        pass
