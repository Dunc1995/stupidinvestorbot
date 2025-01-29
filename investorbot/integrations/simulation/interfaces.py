from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from investorbot.structs.internal import LatestTrade


class ITime(ABC):
    @abstractmethod
    def now(self) -> datetime:
        pass


class IDataProvider(ABC):
    @abstractmethod
    def get_latest_trade(self, coin_name) -> LatestTrade:
        pass

    @abstractmethod
    def get_latest_trades(self) -> List[LatestTrade]:
        pass

    @abstractmethod
    def get_coin_time_series_data(self, coin_name: str) -> dict:
        pass

    @abstractmethod
    def generate_time_series_data(self):
        pass
