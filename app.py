import time
import logging
import math
import os
from chalice import Chalice, Rate
import boto3
from requests.exceptions import HTTPError
from chalicelib.models.app import SellOrder
from chalicelib.models.crypto import Order
from chalicelib.repo import CryptoRepo
from chalicelib.strategies import CoinSelectionStrategies

CRYPTO_KEY = os.environ.get("CRYPTO_KEY")
CRYPTO_SECRET_KEY = os.environ.get("CRYPTO_SECRET_KEY")
CRYPTO_APP_ENVIRONMENT = os.environ.get("CRYPTO_APP_ENVIRONMENT")

INVESTMENT_INCREMENTS = 20.0
MAX_COINS = 4

logger = logging.getLogger()
logger.setLevel("INFO")

app = Chalice(app_name="investorbot")

repo = CryptoRepo(CRYPTO_KEY, CRYPTO_SECRET_KEY)

dynamodb = (
    boto3.resource("dynamodb", endpoint_url="http://dynamodb-local:8000")
    if CRYPTO_APP_ENVIRONMENT == "Development"
    else boto3.resource("dynamodb")
)

order_table = dynamodb.Table("Orders")


def buy_coin_routine():
    user_balance = repo.get_usd_balance()

    logger.info(f"Your balance is ${user_balance}")

    number_of_coins_to_invest = math.floor(float(user_balance) / INVESTMENT_INCREMENTS)

    if number_of_coins_to_invest == 0:
        return  # No action to take if no coins can be selected based on current balance.
    elif number_of_coins_to_invest > MAX_COINS:
        number_of_coins_to_invest = MAX_COINS

    logger.info(
        f"Searching for {number_of_coins_to_invest} coins to invest in at ${INVESTMENT_INCREMENTS} each"
    )

    coin_selection = repo.select_coins_of_interest(
        CoinSelectionStrategies.HIGH_GAIN,
        number_of_coins_to_invest,
        INVESTMENT_INCREMENTS,  #! Not sure I like the investment increments variable being passed here.
    )

    for coin in coin_selection:
        logger.info(f"Selected {coin.name}")

    for order in repo.place_coin_buy_orders(coin_selection):
        order_table.put_item(Item=order.__dict__)


def sell_coin_routine():
    time_now = int(time.time() * 1000)
    response = order_table.scan()
    data = response["Items"]

    orders = [Order(**order_dict) for order_dict in data]
    order_ids_for_deletion = []

    for order in orders:
        order_detail = repo.user.get_order_detail(order.client_oid)
        coin_balance = repo.get_coin_balance(order_detail.fee_instrument_name)

        time_of_order = int(order_detail.create_time)
        milliseconds_since_order = time_now - time_of_order
        hours_since_order = milliseconds_since_order / (1000 * 60 * 60)

        logger.info(
            f"It has been {hours_since_order:g} hours since buy order was placed for order {order.client_oid}."
        )
        logger.info(f"Order status: {order_detail.status}")

        value_ratio = (
            1.01 if hours_since_order < 3.0 else 1.0
        )  # Just try to get money back if holding onto a coin for more than 3 hours.

        logger.info(f"Desired value ratio: {value_ratio}")

        sell_order = SellOrder(coin_balance, order_detail)

        logger.info(sell_order.__dict__)

        if sell_order.coin_quantity_can_be_sold:
            if sell_order.value_ratio > value_ratio:
                logger.info(f"Placing sell order for order {sell_order.buy_order_id}.")

                try:
                    repo.place_coin_sell_order(sell_order)
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
        elif sell_order.buy_order_status == "CANCELED":
            order_ids_for_deletion.append(sell_order.buy_order_id)
        else:
            logger.info(
                f"Ignoring order id {sell_order.buy_order_id} for the time being."
            )

    with order_table.batch_writer() as batch:
        for order_id in order_ids_for_deletion:
            logger.info(
                f"Removing order {order_id} from database as the order is now being sold."
            )
            batch.delete_item(Key={"client_oid": order_id})


@app.schedule(Rate(15, unit=Rate.MINUTES))
def buy_coin_routine_schedule(event):
    buy_coin_routine()


@app.schedule(Rate(5, unit=Rate.MINUTES))
def sell_coin_routine_schedule(event):
    sell_coin_routine()


@app.route("/buy-test")
def buy_coin_routine_schedule_test():
    buy_coin_routine()


@app.route("/sell-test")
def sell_coin_routine_schedule_test():
    sell_coin_routine()
