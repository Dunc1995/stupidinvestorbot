from abc import ABC, abstractmethod
from datetime import datetime


class ITime(ABC):
    @abstractmethod
    def now(self) -> datetime:
        pass
