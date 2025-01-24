from enum import Enum


# TODO strictly speaking this should be under integrations/cryptodotcom/enums.py
# TODO make distinction between app and what cryptodotcom requires
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
