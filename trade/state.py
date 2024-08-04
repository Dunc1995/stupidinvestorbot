from dataclasses import dataclass
from uuid import UUID


@dataclass
class TradeState:
    trade_id: UUID
    buy_order_placed: bool
    buy_order_filled: bool
    coin_quantity: int
    coin_value: float
    sell_order_placed: bool
    sell_order_filled: bool
