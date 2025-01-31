from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Tuple

from investorbot.interfaces.providers import ITimeProvider
from investorbot.structs.internal import LatestTrade


class ITimeSimulation(ITimeProvider):
    """Implement this interface if you need to simulate time in any way."""

    @abstractmethod
    def increment_time(self) -> datetime:
        """This method should only be accessible to whatever is responsible for incrementing
        simulated time."""
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
