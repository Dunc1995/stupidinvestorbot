import time
import logging
import math
from typing import List
from requests.exceptions import HTTPError
from investorbot.constants import INVESTMENT_INCREMENTS, MAX_COINS
from investorbot import crypto_context, app_context
from investorbot.models import CoinProperties
from investorbot.structs.internal import SellOrder
import investorbot.timeseries as timeseries


logger = logging.getLogger()
logger.setLevel("INFO")


def get_coin_data_routine():
    ts_summaries = []

    for coin in crypto_context.market.get_usd_coins():
        logger.info(f"Fetching latest 24hr dataset for {coin.instrument_name}.")

        time_series_data = crypto_context.get_coin_time_series_data(
            coin.instrument_name
        )

        ts_summary = timeseries.get_coin_time_series_summary(
            coin.instrument_name, time_series_data
        )

        ts_summaries.append(ts_summary)

    app_context.add_items(ts_summaries)


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

    # coin_selection = crypto_context.select_coins_of_interest(
    #     CoinSelectionStrategies.HIGH_GAIN, number_of_coins_to_invest
    # )

    # for coin in coin_selection:
    #     logger.info(f"Selected {coin.name}")

    # for order in crypto_context.place_coin_buy_orders(coin_selection):
    #     app_context.add_item(order)


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

    app_context.add_items([CoinProperties(instrument) for instrument in instruments])
