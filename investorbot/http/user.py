import json
import logging
from typing import Dict
import uuid
from investorbot.constants import CRYPTO_USER_URL, DEFAULT_LOGS_NAME
from investorbot.http.base import AuthenticatedHttpClient
from investorbot.structs.ingress import (
    OrderJson,
    OrderDetailJson,
    PositionBalanceJson,
    UserBalanceJson,
)

logger = logging.getLogger(DEFAULT_LOGS_NAME)


class UserHttpClient(AuthenticatedHttpClient):
    def __init__(
        self,
        api_key,
        api_secret_key,
        api_url=CRYPTO_USER_URL,
    ):
        super().__init__(
            id_incr=1, api_key=api_key, api_secret_key=api_secret_key, api_url=api_url
        )

    def get_balance(self) -> UserBalanceJson:
        user_balance = self.post_request("user-balance")[
            0
        ]  # ! zero index assumes only one wallet - may break

        user_balance_obj = UserBalanceJson(**user_balance)

        position_balances = [
            PositionBalanceJson(**position_balance)
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
    ) -> OrderJson:
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

        logger.info(json.dumps(params, indent=4))

        result = self.post_request("create-order", params)

        return OrderJson(**result)

    def get_order_detail(self, client_oid: int) -> OrderDetailJson:
        return OrderDetailJson(
            **self.post_request("get-order-detail", {"client_oid": str(client_oid)})
        )

    def get_trades(self, instrument_name: str) -> dict:
        # TODO See below:
        # I suspect this will be needed if multiple trades are triggered
        # by one buy or sell order. Can remove if the app runs for a decent
        # amount of time without error.

        return self.post_request(
            "get-trades", {"instrument_name": instrument_name, "limit": 20}
        )

    def cancel_order(self, order_id: int):
        return self.post_request("cancel-order", {"client_oid": str(order_id)})
