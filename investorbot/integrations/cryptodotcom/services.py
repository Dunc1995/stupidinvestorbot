import logging
import math
from typing import List
from investorbot.integrations.cryptodotcom import mappings
from investorbot.constants import (
    DEFAULT_LOGS_NAME,
    INVESTMENT_INCREMENTS,
)
from investorbot.integrations.cryptodotcom.constants import (
    CRYPTO_KEY,
    CRYPTO_SECRET_KEY,
)
from investorbot.integrations.cryptodotcom.http.market import MarketHttpClient
from investorbot.integrations.cryptodotcom.http.user import UserHttpClient
from investorbot.interfaces.services import ICryptoService
from investorbot.models import BuyOrder, CoinProperties, SellOrder
from investorbot.structs.egress import CoinPurchase, CoinSale
from investorbot.structs.internal import LatestTrade, OrderDetail, PositionBalance


logger = logging.getLogger(DEFAULT_LOGS_NAME)


class CryptoService(ICryptoService):
    market: MarketHttpClient
    user: UserHttpClient

    def __init__(self):
        self.market = MarketHttpClient()
        self.user = UserHttpClient(CRYPTO_KEY, CRYPTO_SECRET_KEY)

    def get_coin_balance(self, coin_name: str) -> PositionBalance | None:
        wallet_balance = self.user.get_balance()

        name = coin_name.split("_")[0] if "_USD" in coin_name else coin_name

        balance = next(
            (x for x in wallet_balance.position_balances if x.instrument_name == name),
            None,
        )

        return (
            mappings.json_to_position_balance(balance) if balance is not None else None
        )

    def get_usd_balance(self) -> float:
        usd_balance = float(self.get_coin_balance("USD").market_value)

        logger.info(f"Your balance is ${usd_balance}")

        return usd_balance

    def get_total_cash_balance(self) -> float:
        return float(self.user.get_balance().total_cash_balance)

    def get_investable_coin_count(self) -> int:
        total_cash_balance = self.get_total_cash_balance()
        user_balance = self.get_usd_balance()

        percentage_to_invest = (
            user_balance / total_cash_balance - 0.5
        )  # TODO make configurable

        number_of_coins_to_invest = (
            math.floor(user_balance * percentage_to_invest / INVESTMENT_INCREMENTS)
            if percentage_to_invest > 0
            else 0
        )

        return number_of_coins_to_invest

    def get_latest_trade(self, coin_name: str) -> LatestTrade:
        ticker_json = self.market.get_ticker(coin_name)

        return LatestTrade(ticker_json.instrument_name, ticker_json.latest_trade)

    def get_latest_trades(self) -> List[LatestTrade]:
        tickers = self.market.get_usd_tickers()
        trades = [
            LatestTrade(ticker.instrument_name, ticker.latest_trade)
            for ticker in tickers
        ]

        return trades

    def get_coin_time_series_data(self, coin_name: str, hours=24) -> dict:
        return self.market.get_valuation(coin_name, "mark_price", hours)

    def get_order_detail(self, order_id: str) -> OrderDetail:
        order_detail_json = self.user.get_order_detail(order_id)

        return mappings.json_to_order_detail(order_detail_json)

    def get_coin_properties(self) -> List[CoinProperties]:
        instruments = self.market.get_instruments()

        return [
            mappings.json_to_coin_properties(instrument) for instrument in instruments
        ]

    def place_coin_buy_order(self, order_spec: CoinPurchase) -> BuyOrder:

        order = self.user.create_order(
            order_spec.coin_properties.coin_name,
            order_spec.price_per_coin,
            order_spec.quantity,
            "BUY",
        )

        return BuyOrder(
            buy_order_id=order.client_oid,
            coin_name=order_spec.coin_properties.coin_name,
            price_per_coin=order_spec.price_per_coin,
        )

    def place_coin_sell_order(
        self, buy_order_id: str, coin_sale: CoinSale
    ) -> SellOrder:
        order = self.user.create_order(
            coin_sale.coin_properties.coin_name,
            coin_sale.price_per_coin,
            coin_sale.quantity,
            "SELL",
        )

        sell_order = SellOrder(order.client_oid, buy_order_id)

        return sell_order
