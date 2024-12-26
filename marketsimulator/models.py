from typing import List, Optional
from sqlalchemy import Boolean, ForeignKey, String, Integer, Float, Null
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class PositionBalance(Base):
    __tablename__ = "position_balances"

    position_balance_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    instrument_name: Mapped[str] = mapped_column(String())
    quantity: Mapped[float] = mapped_column(Float())
    market_value: Mapped[float] = mapped_column(Float())
    collateral_eligible: Mapped[bool] = mapped_column(Boolean())
    haircut: Mapped[float] = mapped_column(Float())
    collateral_amount: Mapped[float] = mapped_column(Float())
    max_withdrawal_balance: Mapped[float] = mapped_column(Float())
    reserved_qty: Mapped[float] = mapped_column(Float())
    hourly_interest_rate: Mapped[float] = mapped_column(Float())


class UserBalance(Base):
    __tablename__ = "user_balances"

    account_id: Mapped[str] = mapped_column(primary_key=True)
    total_available_balance: Mapped[float] = mapped_column(Float())
    total_margin_balance: Mapped[float] = mapped_column(Float())
    total_initial_margin: Mapped[float] = mapped_column(Float())
    total_position_im: Mapped[float] = mapped_column(Float())
    total_haircut: Mapped[float] = mapped_column(Float())
    total_maintenance_margin: Mapped[float] = mapped_column(Float())
    total_position_cost: Mapped[float] = mapped_column(Float())
    total_cash_balance: Mapped[float] = mapped_column(Float())
    total_collateral_value: Mapped[float] = mapped_column(Float())
    total_session_unrealized_pnl: Mapped[float] = mapped_column(Float())
    instrument_name: Mapped[str] = mapped_column(String())
    total_session_realized_pnl: Mapped[float] = mapped_column(Float())
    is_liquidating: Mapped[bool] = mapped_column(Boolean())
    # credit_limits: Mapped[list] = mapped_column()
    total_effective_leverage: Mapped[float] = mapped_column(Float())
    total_borrow: Mapped[float] = mapped_column(Float())
    position_limit: Mapped[float] = mapped_column(Float())
    used_position_limit: Mapped[float] = mapped_column(Float())
    # position_balances: List[PositionBalance]
    has_risk: Mapped[bool] = mapped_column(Boolean)
    terminatable: Mapped[bool] = mapped_column(Boolean)
    margin_score: Mapped[float] = mapped_column(Float())


class Instrument(Base):
    __tablename__ = "instruments"

    symbol: Mapped[str] = mapped_column(primary_key=True)
    inst_type: Mapped[str] = mapped_column(String())
    display_name: Mapped[str] = mapped_column(String())
    base_ccy: Mapped[str] = mapped_column(String())
    quote_ccy: Mapped[str] = mapped_column(String())
    quote_decimals: Mapped[int] = mapped_column(Integer())
    quantity_decimals: Mapped[int] = mapped_column(Integer())
    price_tick_size: Mapped[str] = mapped_column(String())
    qty_tick_size: Mapped[str] = mapped_column(String())
    max_leverage: Mapped[str] = mapped_column(String())
    tradable: Mapped[str] = mapped_column(String())
    expiry_timestamp_ms: Mapped[int] = mapped_column(Integer())
    beta_product: Mapped[bool] = mapped_column(Boolean())
    margin_buy_enabled: Mapped[bool] = mapped_column(Boolean())
    margin_sell_enabled: Mapped[bool] = mapped_column(Boolean())
    contract_size: Mapped[str] = mapped_column(String(), nullable=True, default=None)
    underlying_symbol: Mapped[str] = mapped_column(
        String(), nullable=True, default=None
    )

    valuation: Mapped[List["ValuationData"]] = relationship(
        back_populates="instrument", cascade="all, delete", init=False
    )


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    client_oid: Mapped[str] = mapped_column(String())


class OrderDetail(Base):
    __tablename__ = "order_details"

    account_id: Mapped[str] = mapped_column(String())
    order_id: Mapped[int] = mapped_column(primary_key=True)
    client_oid: Mapped[int] = mapped_column(Integer())
    order_type: Mapped[str] = mapped_column(String())
    time_in_force: Mapped[str] = mapped_column(String())
    side: Mapped[str] = mapped_column(String())
    # exec_inst: LMapped[ist] = mapped_column(String())
    quantity: Mapped[int] = mapped_column(Integer())
    limit_price: Mapped[str] = mapped_column(String())
    order_value: Mapped[str] = mapped_column(String())
    avg_price: Mapped[str] = mapped_column(String())
    cumulative_quantity: Mapped[str] = mapped_column(String())
    cumulative_value: Mapped[str] = mapped_column(String())
    cumulative_fee: Mapped[str] = mapped_column(String())
    status: Mapped[str] = mapped_column(String())
    update_user_id: Mapped[str] = mapped_column(String())
    order_date: Mapped[str] = mapped_column(String())
    instrument_name: Mapped[str] = mapped_column(String())
    fee_instrument_name: Mapped[str] = mapped_column(String())
    create_time: Mapped[int] = mapped_column(Integer())
    create_time_ns: Mapped[int] = mapped_column(Integer())
    update_time: Mapped[int] = mapped_column(Integer())
    ref_price: Mapped[str] = mapped_column(String())
    reason: Mapped[str] = mapped_column(String())
    maker_fee_rate: Mapped[str] = mapped_column(String())
    taker_fee_rate: Mapped[str] = mapped_column(String())
    ref_price_type: Mapped[str] = mapped_column(String())


class Ticker(Base):
    __tablename__ = "tickers"

    i: Mapped[str] = mapped_column(primary_key=True)
    h: Mapped[str] = mapped_column(String())
    l: Mapped[str] = mapped_column(String())
    a: Mapped[str] = mapped_column(String())
    v: Mapped[str] = mapped_column(String())
    vv: Mapped[str] = mapped_column(String())
    c: Mapped[str] = mapped_column(String())
    b: Mapped[str] = mapped_column(String())
    k: Mapped[str] = mapped_column(String())
    oi: Mapped[str] = mapped_column(String())
    t: Mapped[int] = mapped_column(String())


class ValuationData(Base):
    __tablename__ = "valuation_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    instrument_name: Mapped[str] = mapped_column(
        ForeignKey("instruments.symbol", ondelete="CASCADE")
    )
    t: Mapped[int] = mapped_column(Integer())
    v: Mapped[float] = mapped_column(Float())

    instrument: Mapped[Optional[Instrument]] = relationship(
        back_populates="valuation", init=False
    )

    def to_dict(self) -> dict:
        return {"t": self.t, "v": self.v}
