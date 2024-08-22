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

    @staticmethod
    def from_instrument_json(json_data: InstrumentJson) -> "CoinProperties":
        coin_name = json_data.symbol
        quantity_tick_size = float(json_data.qty_tick_size)
        quantity_decimals = int(json_data.quantity_decimals)
        price_tick_size = float(json_data.price_tick_size)
        price_decimals = int(json_data.quote_decimals)

        return CoinProperties(
            coin_name,
            quantity_tick_size,
            quantity_decimals,
            price_tick_size,
            price_decimals,
        )


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

    market_confidence_id: Mapped[int] = mapped_column(
        ForeignKey("market_confidence.market_confidence_id", ondelete="CASCADE"),
    )

    market_confidence: Mapped[Optional["MarketConfidence"]] = relationship(
        back_populates="ts_data", init=False
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


class MarketConfidence(Base):
    __tablename__ = "market_confidence"

    market_confidence_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )

    confidence_rating_id: Mapped[int] = mapped_column(
        ForeignKey("market_confidence_rating.rating_id", ondelete="CASCADE")
    )

    rating: Mapped[Optional["MarketConfidenceRating"]] = relationship(
        back_populates="confidence_entries", init=False
    )

    ts_data: Mapped[List["TimeSeriesSummary"]] = relationship(
        back_populates="market_confidence",
        cascade="all, delete",
    )


class MarketConfidenceRating(Base):
    __tablename__ = "market_confidence_rating"

    rating_id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String())

    confidence_entries: Mapped[List["MarketConfidence"]] = relationship(
        back_populates="rating", cascade="all, delete", init=False
    )
