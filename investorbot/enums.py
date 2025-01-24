from enum import Enum


class OrderStatus(Enum):
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    OTHER = "OTHER"


class MarketCharacterization(Enum):
    RISING_RAPIDLY = 1
    RISING = 2
    FLAT = 3
    FALLING = 4
    FALLING_RAPIDLY = 5


class TrendLineState(Enum):
    RISING = "RISING"
    FLAT = "FLAT"
    FALLING = "FALLING"
    UNKNOWN = "UNKNOWN"
