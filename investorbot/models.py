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
