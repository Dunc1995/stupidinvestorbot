from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import MappedAsDataclass

from investorbot.structs.ingress import InstrumentJson


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class CoinProperties(Base):
    __tablename__ = "coin_properties"

    coin_name: Mapped[str] = mapped_column(primary_key=True)
    quantity_tick_size: Mapped[float] = mapped_column(Float())
    quantity_decimals: Mapped[int] = mapped_column(Integer())
    price_tick_size: Mapped[float] = mapped_column(Float())
    price_decimals: Mapped[int] = mapped_column(Integer())

    buy_orders: Mapped[List["BuyOrder"]] = relationship(
        init=False, back_populates="coin_properties", cascade="all, delete-orphan"
    )

    def __init__(self, json_data: InstrumentJson):
        self.coin_name = json_data.symbol
        self.quantity_tick_size = float(json_data.qty_tick_size)
        self.quantity_decimals = int(json_data.quantity_decimals)
        self.price_tick_size = float(json_data.price_tick_size)
        self.price_decimals = int(json_data.quote_decimals)


class BuyOrder(Base):
    __tablename__ = "buy_orders"

    buy_order_id: Mapped[str] = mapped_column(primary_key=True)
    coin_name: Mapped[str] = mapped_column(ForeignKey("coin_properties.coin_name"))
    coin_properties: Mapped[Optional[CoinProperties]] = relationship(
        init=False, back_populates="buy_orders"
    )


class TimeSeriesSummary(Base):
    """Data container for storing basic statistical properties after
    analyzing valuation data for a particular coin.
    """

    __tablename__ = "time_series_data"

    summary_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    coin_name: Mapped[str] = mapped_column(String())
    mean: Mapped[float] = mapped_column(Float())
    std: Mapped[float] = mapped_column(Float())
    percentage_std: Mapped[float] = mapped_column(Float())
    line_of_best_fit_coefficient: Mapped[float] = mapped_column(Float())
    line_of_best_fit_offset: Mapped[float] = mapped_column(Float())
    time_offset: Mapped[int] = mapped_column(Integer())
    creation_time_ms: Mapped[int] = mapped_column(Integer())

    modes: Mapped[List["TimeSeriesMode"]] = relationship(
        back_populates="summary",
        cascade="all, delete",
    )


class TimeSeriesMode(Base):
    __tablename__ = "time_series_data_modes"

    mode_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    summary_id: Mapped[int] = mapped_column(
        ForeignKey("time_series_data.summary_id", ondelete="CASCADE"), init=False
    )
    mode: Mapped[float] = mapped_column(Float())
    summary: Mapped[Optional[TimeSeriesSummary]] = relationship(
        back_populates="modes", init=False
    )
