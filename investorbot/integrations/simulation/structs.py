from dataclasses import dataclass


@dataclass
class PositionBalanceAdjustmentResult:
    cumulative_value: float
    cumulative_quantity: float
    net_value: float
    net_quantity: float
    fee_amount: float
    fee_currency: str
