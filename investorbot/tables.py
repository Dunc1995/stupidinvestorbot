from typing import List, Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class CoinProperties(Base):
    __tablename__ = "coin_properties"

    coin_name: Mapped[str] = mapped_column(primary_key=True)
    quantity_tick_size: Mapped[str] = mapped_column(String(30))
    quantity_decimals: Mapped[str] = mapped_column(String(30))
    price_tick_size: Mapped[str] = mapped_column(String(30))
    price_decimals: Mapped[str] = mapped_column(String(30))

    buy_orders: Mapped[List["BuyOrder"]] = relationship(
        init=False, back_populates="coin_properties", cascade="all, delete-orphan"
    )


class BuyOrder(Base):
    __tablename__ = "buy_orders"

    buy_order_id: Mapped[str] = mapped_column(primary_key=True)
    coin_name: Mapped[str] = mapped_column(String(30))

    coin_properties_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("coin_properties.coin_name"), init=False
    )
    coin_properties: Mapped[Optional[CoinProperties]] = relationship(
        init=False, back_populates="buy_orders"
    )
