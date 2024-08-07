from typing import Dict, List
import uuid
from chalicelib.http.base import AuthenticatedHttpClient
from chalicelib.models.app import CoinSummary
from chalicelib.models.crypto import (
    ListResponse,
    Order,
    OrderDetail,
    PositionBalance,
    UserBalance,
)


class UserHttpClient(AuthenticatedHttpClient):
    def __init__(
        self,
        api_key,
        api_secret_key,
        api_url="https://api.crypto.com/exchange/v1/private/",
    ):
        super().__init__(
            id_incr=1, api_key=api_key, api_secret_key=api_secret_key, api_url=api_url
        )

    def get_balance(self) -> UserBalance:
        user_balance = self.post_request("user-balance")[
            0
        ]  # ! zero index assumes only one wallet - may break

        user_balance_obj = UserBalance(**user_balance)

        position_balances = [
            PositionBalance(**position_balance)
            for position_balance in user_balance_obj.position_balances
        ]

        user_balance_obj.position_balances = position_balances

        return user_balance_obj

    def get_create_order_params(
        self,
        instrument_name: str,
        instrument_price_usd: str,
        quantity: str,
        side: str,
    ) -> Dict:
        return {
            "client_oid": str(uuid.uuid4()),
            "instrument_name": instrument_name,
            "side": side,
            "type": "LIMIT",
            "price": f"{instrument_price_usd}",
            "quantity": f"{quantity}",
            "time_in_force": "GOOD_TILL_CANCEL",
        }

    def create_order(
        self,
        instrument_name: str,
        instrument_price_usd: str,
        quantity: str,
        side: str,
    ) -> Order:
        """Creates a buy or sell order for a specific coin. Quantity has to be a multiple of the coin's
        quantity tick size.

        Args:
            instrument_name (str): Name of the crypto coin.
            instrument_price_usd (float): Specific crypto coin price.
            quantity (str): Number of coins to buy or sell.
            side (str): BUY or SELL.

        Returns:
            Dict: response from the buy or sell order.
        """

        params = self.get_create_order_params(
            instrument_name, instrument_price_usd, quantity, side
        )

        result = self.post_request("create-order", params)

        return Order(**result)

    def get_order_detail(self, order_id: int) -> OrderDetail:
        return OrderDetail(
            **self.post_request("get-order-detail", {"order_id": str(order_id)})
        )

    def cancel_order(self, order_id: int):
        return self.post_request("cancel-order", {"order_id": str(order_id)})
