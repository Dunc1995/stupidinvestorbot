from dataclasses import dataclass
from uuid import UUID


@dataclass
class TradeState:
    trade_id: UUID
    buy_order_placed: bool
    buy_order_filled: bool
    sell_order_placed: bool
    sell_order_filled: bool


@dataclass
class TradeMetaData(TradeState):
    coin_quantity: int
    coin_value: float
