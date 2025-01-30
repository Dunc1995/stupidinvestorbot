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
    fee: Mapped[float] = mapped_column(Float())
    fee_currency: Mapped[str] = mapped_column(String())


class PositionBalanceSimulated(TimestampMixin, SimulationBase):

    __tablename__ = "position_balances"

    balance_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    coin_name: Mapped[str] = mapped_column()
    quantity: Mapped[float] = mapped_column(Float())
    reserved_quantity: Mapped[float] = mapped_column(Float())
