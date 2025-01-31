from enum import StrEnum


class OrderDetailStatus(StrEnum):
    NEW = "NEW"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    FILLED = "FILLED"
    EXPIRED = "EXPIRED"
