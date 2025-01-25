from sqlalchemy import Column, DateTime, Float, func, String
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import MappedAsDataclass


class SimulationBase(MappedAsDataclass, DeclarativeBase):
    pass


class TimestampMixin(object):
    time_creates_ms = Column(DateTime, default=func.now())


class OrderDetailSimulated(TimestampMixin, SimulationBase):

    __tablename__ = "order_details"

    status: Mapped[str] = mapped_column(String())
    order_id: Mapped[str] = mapped_column(primary_key=True)
    coin_name: Mapped[str] = mapped_column(String())
    order_value: Mapped[float] = mapped_column(Float())
    quantity: Mapped[float] = mapped_column(Float())
    cumulative_quantity: Mapped[float] = mapped_column(Float())
    cumulative_value: Mapped[float] = mapped_column(Float())
    cumulative_fee: Mapped[float] = mapped_column(Float())
    fee_currency: Mapped[str] = mapped_column(String())


class PositionBalanceSimulated(SimulationBase):

    __tablename__ = "position_balances"

    coin_name: Mapped[str] = mapped_column(primary_key=True)
    # TODO don't dedicate a column to market value as fluctuations in market value need to reflect latest prices
    market_value: Mapped[float] = mapped_column(Float())
    quantity: Mapped[float] = mapped_column(Float())
    reserved_quantity: Mapped[float] = mapped_column(Float())
