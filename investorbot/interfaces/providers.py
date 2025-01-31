from abc import ABC, abstractmethod
from datetime import datetime


class ITimeProvider(ABC):
    """Implement this provider for when time properties need to be customized. This allows the
    investor bot to pretend to trade at a faster or slower pace than it would whilst running in
    reality. This is abstraction is mainly for simulation and testing purposes."""

    @abstractmethod
    def now(self) -> datetime:
        pass

    @abstractmethod
    def now_in_ms(self) -> int:
        pass
