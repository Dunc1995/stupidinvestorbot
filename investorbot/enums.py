from enum import Enum


class OrderStatus(Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    FILLED = "FILLED"
    EXPIRED = "EXPIRED"


class ConfidenceRating(Enum):
    HIGH_CONFIDENCE = 1
    MODERATE_CONFIDENCE = 2
    UNDECIDED = 3
    LITTLE_CONFIDENCE = 4
    NO_CONFIDENCE = 5


class TrendLineState(Enum):
    RISING = "RISING"
    FLAT = "FLAT"
    FALLING = "FALLING"
    UNKNOWN = "UNKNOWN"
