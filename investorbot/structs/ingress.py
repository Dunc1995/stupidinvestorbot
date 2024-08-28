from dataclasses import dataclass
from typing import List


@dataclass
class PositionBalanceJson:
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
class UserBalanceJson:
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
    position_balances: List[PositionBalanceJson]
    has_risk: bool
    terminatable: bool
    margin_score: float


@dataclass
class InstrumentJson:
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
class OrderJson:
    """Basic parameters that are returned when calling private/create-order"""

    order_id: int
    client_oid: str


@dataclass
class OrderDetailJson:
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


@dataclass
class TickerJson:
    """Maps abbreviated property names from public/get-tickers query to human readable
    properties."""

    instrument_name: str
    highest_trade_24h: str
    lowest_trade_24h: str
    latest_trade: str
    total_traded_volume_24h: str
    total_traded_volume_usd_24h: str
    percentage_change_24h: str
    best_bid_price: str
    best_ask_price: str
    open_interest: str
    timestamp: int

    def __init__(self, obj):
        self.instrument_name = obj["i"]
        self.highest_trade_24h = obj["h"]
        self.lowest_trade_24h = obj["l"]
        self.latest_trade = obj["a"]
        self.total_traded_volume_24h = obj["v"]
        self.total_traded_volume_usd_24h = obj["vv"]
        self.percentage_change_24h = obj["c"]
        self.best_bid_price = obj["b"]
        self.best_ask_price = obj["k"]
        self.open_interest = obj["oi"]
        self.timestamp = obj["t"]
