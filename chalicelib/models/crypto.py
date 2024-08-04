from dataclasses import dataclass
from typing import List


@dataclass
class PositionBalance:
    instrument_name: str
    quantity: float
    market_value: float
    collateral_eligible: bool
    haircut: float
    collateral_amount: float
    max_withdrawal_balance: float
    reserved_qty: float
    hourly_interest_rate: float


@dataclass
class UserBalance:
    total_available_balance: float
    total_margin_balance: float
    total_initial_margin: float
    total_position_im: float
    total_haircut: float
    total_maintenance_margin: float
    total_position_cost: float
    total_cash_balance: float
    total_collateral_value: float
    total_session_unrealized_pnl: float
    instrument_name: str
    total_session_realized_pnl: float
    is_liquidating: bool
    credit_limits: list
    total_effective_leverage: float
    total_borrow: float
    position_limit: float
    used_position_limit: float
    position_balances: list[PositionBalance]
    has_risk: bool
    terminatable: bool
    margin_score: float


@dataclass
class Instrument:
    """Expected parameters when calling public/get-instruments.
    At the moment I only really want qty_tick_size from these objects.
    Price tick size is probably also important."""

    symbol: str
    inst_type: str
    display_name: str
    base_ccy: str
    quote_ccy: str
    quote_decimals: int
    quantity_decimals: int
    price_tick_size: str
    qty_tick_size: str
    max_leverage: str
    tradable: str
    expiry_timestamp_ms: int
    beta_product: bool
    margin_buy_enabled: bool
    margin_sell_enabled: bool
    contract_size: str = None
    underlying_symbol: str = None


@dataclass
class Order:
    """Basic parameters that are returned when calling private/create-order"""

    order_id: int
    client_oid: str


@dataclass
class OrderDetail:
    account_id: str
    order_id: int
    client_oid: int
    order_type: str
    time_in_force: str
    side: str
    exec_inst: List
    quantity: int
    limit_price: str
    order_value: str
    avg_price: str
    cumulative_quantity: str
    cumulative_value: str
    cumulative_fee: str
    status: str
    update_user_id: str
    order_date: str
    instrument_name: str
    fee_instrument_name: str
    create_time: int
    create_time_ns: int
    update_time: int
    ref_price: str
    reason: str
    maker_fee_rate: str = None
    taker_fee_rate: str = None
    ref_price_type: str = None

    @property
    def successful(self) -> bool:
        """
        Returns:
            bool: Returns True if the order has been fulfilled completely.
        """
        return self.status == "FILLED"
