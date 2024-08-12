import time
import logging
import math
from requests.exceptions import HTTPError
from investorbot.constants import INVESTMENT_INCREMENTS, MAX_COINS
from investorbot import crypto_context, app_context
from investorbot.structs.internal import SellOrder
from investorbot.structs.ingress import OrderJson
from investorbot.strategies import CoinSelectionStrategies
import investorbot.structs.transforms as transforms


logger = logging.getLogger()
logger.setLevel("INFO")


def buy_coin_routine():
    user_balance = crypto_context.get_usd_balance()

    logger.info(f"Your balance is ${user_balance}")

    number_of_coins_to_invest = math.floor(float(user_balance) / INVESTMENT_INCREMENTS)

    if number_of_coins_to_invest == 0:
        return  # No action to take if no coins can be selected based on current balance.
    elif number_of_coins_to_invest > MAX_COINS:
        number_of_coins_to_invest = MAX_COINS

    logger.info(
        f"Searching for {number_of_coins_to_invest} coins to invest in at ${INVESTMENT_INCREMENTS} each"
    )

    coin_selection = crypto_context.select_coins_of_interest(
        CoinSelectionStrategies.HIGH_GAIN, number_of_coins_to_invest
    )

    for coin in coin_selection:
        logger.info(f"Selected {coin.name}")

    for order in crypto_context.place_coin_buy_orders(coin_selection):
        app_context.add_item(order)


def sell_coin_routine():
    buy_orders = app_context.get_all_buy_orders()

    for order in buy_orders:
        order_detail = crypto_context.get_order_detail(order.client_oid)

        coin_balance = crypto_context.get_coin_balance(order_detail.fee_instrument_name)

        sell_order = SellOrder(coin_balance, order_detail)

        logger.info(sell_order.__dict__)

        if sell_order.value_ratio >= order_detail.minimum_acceptable_value_ratio:
            logger.info(f"Placing sell order for order {sell_order.buy_order_id}.")

            try:
                crypto_context.place_coin_sell_order(sell_order)
            except HTTPError as error:
                logger.warn(
                    "WARNING HTTP ERROR - continuing with script to ensure database consistency."
                )
                logger.warn(error.args[0])


def init_db():
    app_context.run_migration()

    instruments = crypto_context.market.get_instruments()

    coin_properties = transforms.get_coin_properties_from_instruments(instruments)

    app_context.add_items(coin_properties)
