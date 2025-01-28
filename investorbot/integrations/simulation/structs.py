from dataclasses import dataclass


@dataclass
class PositionBalanceAdjustmentResult:
    total_value: float
    quantity: float
    net_value: float
    net_quantity: float
    fee_amount: float
    fee_currency: str


@dataclass
class ValuationData:
    instrument_name: str
    t: int
    v: float
