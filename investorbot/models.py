from typing import List, Optional
from sqlalchemy import Boolean, ForeignKey, String, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class CoinProperties(Base):
    """The Crypto API requires order quantities and order values to be rounded according to "tick
    sizes" for coin price and coin quantities. There's no way to request these properties for coins
    individually, so here it is easier to query the data whilst initialising the database and then
    storing the data internally.
    """

    __tablename__ = "coin_properties"

    coin_name: Mapped[str] = mapped_column(primary_key=True)
    quantity_tick_size: Mapped[float] = mapped_column(Float())
    quantity_decimals: Mapped[int] = mapped_column(Integer())
    price_tick_size: Mapped[float] = mapped_column(Float())
    price_decimals: Mapped[int] = mapped_column(Integer())

    buy_orders: Mapped[List["BuyOrder"]] = relationship(
        init=False, back_populates="coin_properties", cascade="all, delete-orphan"
    )


class BuyOrder(Base):
    """When an order has been placed, we want to store the associated GUID id so the app can track
    the state of the order."""

    __tablename__ = "buy_orders"

    buy_order_id: Mapped[str] = mapped_column(primary_key=True)
    coin_name: Mapped[str] = mapped_column(ForeignKey("coin_properties.coin_name"))
    price_per_coin: Mapped[float] = mapped_column(Float())
    coin_properties: Mapped[Optional[CoinProperties]] = relationship(
        init=False, back_populates="buy_orders"
    )

    sell_order: Mapped[Optional["SellOrder"]] = relationship(
        init=False, back_populates="buy_order"
    )


class SellOrder(Base):
    """As with tracking BUY orders, SELL orders also need to be tracked incase orders are
    unsuccessful or end up cancelled."""

    __tablename__ = "sell_orders"

    sell_order_id: Mapped[str] = mapped_column(primary_key=True)
    buy_order_id: Mapped[str] = mapped_column(ForeignKey("buy_orders.buy_order_id"))

    buy_order: Mapped[Optional[BuyOrder]] = relationship(
        init=False, back_populates="sell_order"
    )


class TimeSeriesSummary(Base):
    """Data container for storing basic statistical properties after analyzing time series data for
    a particular coin."""

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

    modes: Mapped[List["TimeSeriesMode"]] = relationship(
        back_populates="summary",
        cascade="all, delete",
    )

    market_analysis_id: Mapped[int] = mapped_column(
        ForeignKey("market_analysis.market_analysis_id", ondelete="CASCADE"), init=False
    )

    market_analysis: Mapped[Optional["MarketAnalysis"]] = relationship(
        back_populates="ts_data", init=False
    )


class TimeSeriesMode(Base):
    """Time series analysis can produce multiple modes for a given dataset. This is represented by
    the one-to-many relationship between TimeSeriesSummary and TimeSeriesMode models."""

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


class MarketAnalysis(Base):
    """Market analysis, as the name suggests, stores data relating to averaged values across all
    coins. The confidence rating for a given analysis then determines how the app proceeds to
    invest."""

    __tablename__ = "market_analysis"

    market_analysis_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )

    confidence_rating_id: Mapped[int] = mapped_column(
        ForeignKey("coin_selection_criteria.rating_id", ondelete="CASCADE")
    )

    creation_time_ms: Mapped[int] = mapped_column(Integer())

    rating: Mapped[Optional["CoinSelectionCriteria"]] = relationship(
        back_populates="confidence_entries", init=False
    )

    ts_data: Mapped[List["TimeSeriesSummary"]] = relationship(
        back_populates="market_analysis",
        cascade="all, delete",
    )


class CoinSelectionCriteria(Base):
    """Coin selection criteria can be used to configure the app's decision-making process to invest
    in particular coins. Used in conjunction with the app's market analysis, it is able to perform a
    change of tack depending on current market conditions - e.g. if all coins are performing poorly
    then don't invest at all."""

    __tablename__ = "coin_selection_criteria"

    rating_id: Mapped[int] = mapped_column(primary_key=True)

    rating_description: Mapped[str] = mapped_column(String())
    rating_upper_threshold: Mapped[float] = mapped_column(Float())
    rating_upper_unbounded: Mapped[bool] = mapped_column(Boolean())
    rating_lower_threshold: Mapped[float] = mapped_column(Float())
    rating_lower_unbounded: Mapped[bool] = mapped_column(Boolean())

    trade_needs_to_be_within_mean_and_upper_bound: Mapped[bool] = mapped_column(
        Boolean()
    )
    trade_needs_to_be_within_mean_and_lower_bound: Mapped[bool] = mapped_column(
        Boolean()
    )
    standard_deviation_threshold_should_exceed_threshold: Mapped[bool] = mapped_column(
        Boolean()
    )
    standard_deviation_threshold: Mapped[float] = mapped_column(Float())
    trend_line_percentage_threshold: Mapped[float] = mapped_column(Float())
    """Trend line percentage threshold is used to characterise whether a line is rising, falling or
    flat."""
    trend_line_should_be_flat: Mapped[bool] = mapped_column(Boolean())
    trend_line_should_be_rising: Mapped[bool] = mapped_column(Boolean())
    trend_line_should_be_falling: Mapped[bool] = mapped_column(Boolean())
    trend_line_should_be_flat_or_rising: Mapped[bool] = mapped_column(Boolean())

    confidence_entries: Mapped[List["MarketAnalysis"]] = relationship(
        back_populates="rating", cascade="all, delete", init=False
    )
