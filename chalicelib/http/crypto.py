import logging
import datetime as dt
import uuid
import pandas as pd

from chalicelib.strategies import CoinSelection  #! FIXME
from chalicelib.http.market import MarketHttpClient
from chalicelib.http.user import UserHttpClient
from chalicelib.models.app import CoinSummary, TradingStatus, Ticker
from chalicelib.models.crypto import PositionBalance, UserBalance


logger = logging.getLogger("client")


class CryptoHttpClient:
    market: MarketHttpClient
    user: UserHttpClient

    def __init__(self, api_key, api_secret_key):
        self.market = MarketHttpClient()
        self.user = UserHttpClient(api_key, api_secret_key)

    def get_coin_summary(self, coin: Ticker) -> CoinSummary:
        time_series_data = self.market.get_valuation(coin.instrument_name, "mark_price")

        df = pd.DataFrame.from_dict(time_series_data)
        df["t"] = df["t"].apply(lambda x: dt.datetime.fromtimestamp(x / 1000))
        df["v"] = df["v"].astype(float)

        stats = df
        mean = stats["v"].mean()
        std = stats["v"].std()
        modes = stats["v"].mode()
        percentage_std = float(std) / float(mean)

        return CoinSummary(
            name=coin.instrument_name,
            latest_trade=float(coin.latest_trade),
            mean_24h=mean,
            modes_24h=modes,
            std_24h=std,
            percentage_std_24h=percentage_std,
            percentage_change_24h=float(coin.percentage_change_24h),
            is_greater_than_mean=bool(float(coin.latest_trade) - mean > 0),
            is_greater_than_std=bool(float(coin.latest_trade) - (mean + std) > 0),
        )

    def get_coin_balance(self, coin_name: str) -> PositionBalance | None:
        name = coin_name.split("_")[0]
        balance_dict = self.user.get_balance()

        balance = UserBalance(**balance_dict)

        coin_balance = next(
            (
                PositionBalance(**ub)
                for ub in balance.position_balances
                if PositionBalance(**ub).instrument_name == name
            ),
            None,
        )

        return coin_balance

    def select_coin(self, strategy) -> CoinSummary | None:
        coin_summary = None

        for coin in self.market.get_usd_coins():
            logger.info(f"Fetching latest 24hr dataset for {coin.instrument_name}.")

            summary = self.get_coin_summary(coin)

            if CoinSelection.should_select_coin(summary, strategy):
                logger.info(f"Selecting the following coin: {summary}")
                coin_summary = summary
                break
            else:
                logger.info(f"Rejecting the following: {summary}")

        return coin_summary

    def buy_order(
        self,
        instrument_name: str,
        total_price_usd: str,
        latest_trade_price_usd: str,
        tick: str,
        strategy: str,
        dry_run: bool = True,
    ) -> TradingStatus:
        """Purchase a coin with respect to a total investment amount (e.g I want to purchase 20 dollars worth of Bitcoin)

        Args:
            instrument_name (str): Name of the coin to purchase
            total_price_usd (float): Total cost of the investment (e.g. $20)
            latest_trade_price_usd (float): Price per coin (in USD)
            tick (float): Minimum quantity increment of the coin.
            dry_run (bool, optional): Defaults to True. Set to False to actually purchase coins.

        Returns:
            OrderSummary: _description_
        """

        order_summary = None

        quantity = utils.get_coin_quantity(
            latest_trade_price_usd, total_price_usd, tick
        )

        if not dry_run:
            order = self.user.create_order(
                instrument_name, latest_trade_price_usd, quantity, "BUY"
            )

            order_summary = TradingStatus(
                order_id=order.order_id,
                client_oid=order.client_oid,
                coin_name=instrument_name,
                per_coin_price=latest_trade_price_usd,
                is_running=True,
                sell_strategy=strategy,
                _quantity=quantity,
                _initial_quantity=quantity,
            )
        else:
            order_summary = TradingStatus(
                order_id=-1,
                client_oid=str(uuid.uuid4()),
                coin_name=instrument_name,
                per_coin_price=latest_trade_price_usd,
                is_running=True,
                sell_strategy=strategy,
                _quantity=quantity,
                _initial_quantity=quantity,
            )

        return order_summary
