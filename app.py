import logging
import math
import os
from chalice import Chalice, Rate
import boto3
from chalicelib.models.app import SellOrder
from chalicelib.models.crypto import Order
from chalicelib.repo import CryptoRepo
from chalicelib.strategies import CoinSelectionStrategies

CRYPTO_KEY = os.environ.get("CRYPTO_KEY")
CRYPTO_SECRET_KEY = os.environ.get("CRYPTO_SECRET_KEY")
CRYPTO_APP_ENVIRONMENT = os.environ.get("CRYPTO_APP_ENVIRONMENT")

INVESTMENT_INCREMENTS = 20.0
MAX_COINS = 2

logging.basicConfig(level=logging.INFO)
app = Chalice(app_name="investorbot")

repo = CryptoRepo(CRYPTO_KEY, CRYPTO_SECRET_KEY)

dynamodb = (
    boto3.resource("dynamodb", endpoint_url="http://localhost:8000")
    if CRYPTO_APP_ENVIRONMENT == "Development"
    else boto3.resource("dynamodb")
)

order_table = dynamodb.Table("Orders")


def buy_coin_routine():
    user_balance = repo.get_usd_balance()

    number_of_coins_to_invest = math.floor(float(user_balance) / INVESTMENT_INCREMENTS)

    if number_of_coins_to_invest == 0:
        return  # No action to take if no coins can be selected based on current balance.
    elif number_of_coins_to_invest > MAX_COINS:
        number_of_coins_to_invest = MAX_COINS

    coin_selection = repo.select_coins_of_interest(
        CoinSelectionStrategies.HIGH_GAIN,
        number_of_coins_to_invest,
        INVESTMENT_INCREMENTS,  #! Not sure I like the investment increments variable being passed here.
    )

    for order in repo.place_coin_buy_orders(coin_selection):
        order_table.put_item(Item=order.__dict__)


def sell_coin_routine():
    response = order_table.scan()
    data = response["Items"]

    orders = [Order(**order_dict) for order_dict in data]
    order_ids_for_deletion = []

    for order in orders:
        order_detail = repo.user.get_order_detail(order.client_oid)
        coin_balance = repo.get_coin_balance(order_detail.fee_instrument_name)

        sell_order = SellOrder(coin_balance, order_detail)

        if sell_order.value_ratio > 1.01 and sell_order.coin_quantity_can_be_sold:
            repo.place_coin_sell_order(sell_order)
            order_ids_for_deletion.append(sell_order.buy_order_id)

    with order_table.batch_writer() as batch:
        for order_id in order_ids_for_deletion:
            batch.delete_item(Key={"client_oid": order_id})


@app.schedule(Rate(15, unit=Rate.MINUTES))
def buy_coin_routine_schedule(event):
    buy_coin_routine()


@app.schedule(Rate(15, unit=Rate.MINUTES))
def sell_coin_routine_schedule(event):
    sell_coin_routine()
