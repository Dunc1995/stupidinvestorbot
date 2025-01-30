from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Tuple

from investorbot.structs.internal import LatestTrade


class ITime(ABC):
    @abstractmethod
    def now(self) -> datetime:
        pass

    @abstractmethod
    def now_in_ms(self) -> int:
        pass

    @abstractmethod
    def increment_time(self) -> datetime:
        pass


class IDataProvider(ABC):

    @property
    @abstractmethod
    def current_ticker_values(self) -> Tuple[dict, datetime]:
        pass

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

    @abstractmethod
    def increment_ts_data(self) -> Tuple[dict, datetime]:
        pass

    @abstractmethod
    def run_in_real_time(self) -> None:
        pass

    @property
    @abstractmethod
    def time(self) -> ITime:
        pass
