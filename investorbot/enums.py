from enum import Enum


class OrderStatus(Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    FILLED = "FILLED"
    EXPIRED = "EXPIRED"


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
