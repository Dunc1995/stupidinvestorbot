from dataclasses import dataclass
import time

from pandas import Series
from chalicelib.models.crypto import Order


@dataclass
class Ticker:
    """Maps abbreviated property names from public/get-tickers query to human readable properties."""

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


@dataclass
class CoinSummary:
    """Data container for storing basic statistical properties after
    analyzing valuation data for a particular coin.
    """

    name: str
    latest_trade: float
    mean_24h: float
    modes_24h: Series
    std_24h: float
    percentage_change_24h: float
    percentage_std_24h: float
    is_greater_than_mean: bool
    is_greater_than_std: bool

    @property
    def has_few_modes(self) -> bool:
        """Potentially useful if a low number of modes signifies a fairly stable coin resembling
        "white noise" variability.

        Returns:
            bool: True if low number of modes for the given dataset.
        """
        return len(self.modes_24h) < 5

    @property
    def has_high_std(self) -> bool:
        """Useful to work out which coins are the most volatile at any point in time.

        Returns:
            bool: True if standard deviation is higher than the given threshold.
        """
        return self.percentage_std_24h > 0.04

    @property
    def has_low_change(self) -> bool:
        """I'm assuming it's a safe assumption that a volatile coin at its mean or lower than average
        will hopefully have a rebound back to a value above its mean. Use this property to invest at the
        average price or lower.

        Returns:
            bool: True if percentage change is close to zero.
        """
        return self.percentage_change_24h < 0.03 and self.percentage_change_24h > -0.03


@dataclass
class TradingStatus(Order):
    coin_name: str
    per_coin_price: float
    is_running: bool
    sell_strategy: str
    _quantity: float = None
    _buy_order_created: bool = False
    _buy_order_fulfilled: bool = False
    _sell_order_created: bool = False
    _sell_order_fulfilled: bool = False
    _timestamp: int = None
    _initial_quantity: float = None

    @property
    def buy_order_created(self) -> bool:
        return self._buy_order_created

    @property
    def buy_order_fulfilled(self) -> bool:
        return self._buy_order_fulfilled

    @property
    def sell_order_created(self) -> bool:
        return self._sell_order_created

    @property
    def sell_order_fulfilled(self) -> bool:
        return self._sell_order_fulfilled

    @buy_order_created.setter
    def buy_order_created(self, x) -> bool:
        self._buy_order_created = x

    @buy_order_fulfilled.setter
    def buy_order_fulfilled(self, x) -> bool:
        if x is True:
            self._buy_order_created = x

        self._buy_order_fulfilled = x

    @sell_order_created.setter
    def sell_order_created(self, x) -> bool:
        if x is True:
            self._buy_order_created = x
            self._buy_order_fulfilled = x

        self._sell_order_created = x

    @sell_order_fulfilled.setter
    def sell_order_fulfilled(self, x) -> bool:
        if x is True:
            self._buy_order_created = x
            self._buy_order_fulfilled = x
            self._sell_order_created = x

        self._sell_order_fulfilled = x

    @property
    def is_resumable(self):
        # TODO this criteria doesn't cover all edge cases in which it's possible to resume the trade
        return (
            self._buy_order_created
            and self._buy_order_fulfilled
            and not self.sell_order_created
        )

    @property
    def quantity(self):
        if self._quantity is None:
            raise ValueError("Quantity has not been set.")

        return self._quantity

    @property
    def initial_quantity(self):
        return self._initial_quantity

    @quantity.setter
    def quantity(self, x):
        if self._initial_quantity is None:
            self._initial_quantity = x

        self._quantity = x

    @property
    def total_usd(self):
        return float(self.quantity) * float(self.per_coin_price)

    @property
    def timestamp(self) -> int:
        if self._timestamp is None:
            self._timestamp = int(time.time())

        return self._timestamp
