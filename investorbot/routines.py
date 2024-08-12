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
    print("EGG")
    time_now = int(time.time() * 1000)
    response = order_table.scan()
    data = response["Items"]

    orders = [OrderJson(**order_dict) for order_dict in data]
    order_ids_for_deletion = []

    for order in orders:
        order_detail = crypto_context.user.get_order_detail(order.client_oid)

        time_of_order = int(order_detail.create_time)
        milliseconds_since_order = time_now - time_of_order
        hours_since_order = milliseconds_since_order / (1000 * 60 * 60)

        if order_detail.status == "ACTIVE":
            # float(order_detail.cumulative_quantity) < 0.01 * float(
            #     order_detail.quantity
            # )
            continue

        coin_balance = crypto_context.get_coin_balance(order_detail.fee_instrument_name)

        logger.info(
            f"It has been {hours_since_order:g} hours since buy order was placed for order {order.client_oid}."
        )
        logger.info(f"Order status: {order_detail.status}")

        value_ratio = 0.98 + 0.03 ** ((0.01 * hours_since_order) + 1.0)

        logger.info(f"Desired value ratio: {value_ratio}")

        sell_order = SellOrder(coin_balance, order_detail)

        logger.info(sell_order.__dict__)

        if sell_order.value_ratio > value_ratio:
            logger.info(f"Placing sell order for order {sell_order.buy_order_id}.")

            try:
                crypto_context.place_coin_sell_order(sell_order)
                order_ids_for_deletion.append(sell_order.buy_order_id)
            except HTTPError as error:
                logger.warn(
                    "WARNING HTTP ERROR - continuing with script to ensure database consistency."
                )
                logger.warn(error.args[0])
        else:
            logger.info(
                f"Sell order for {sell_order.buy_order_id} is currently pending. Value ratio is insufficient at {sell_order.value_ratio}."
            )


def init_db():
    app_context.run_migration()

    instruments = crypto_context.market.get_instruments()

    coin_properties = transforms.get_coin_properties_from_instruments(instruments)

    app_context.add_items(coin_properties)
