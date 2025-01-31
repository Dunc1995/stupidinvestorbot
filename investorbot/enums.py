from enum import IntEnum, StrEnum


class AppIntegration(StrEnum):
    SIMULATED = "SIMULATED"
    CRYPTODOTCOM = "CRYPTODOTCOM"


class OrderStatus(StrEnum):
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    OTHER = "OTHER"


class MarketCharacterization(IntEnum):
    RISING_RAPIDLY = 1
    RISING = 2
    FLAT = 3
    FALLING = 4
    FALLING_RAPIDLY = 5


class TrendLineState(StrEnum):
    RISING = "RISING"
    FLAT = "FLAT"
    FALLING = "FALLING"
    UNKNOWN = "UNKNOWN"
