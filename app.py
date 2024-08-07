import logging
import math
import os
from chalice import Chalice, Rate
import boto3
from chalicelib.models.crypto import Order
from chalicelib.repo import CryptoRepo
from chalicelib.strategies import CoinSelectionStrategies

CRYPTO_KEY = os.environ.get("CRYPTO_KEY")
CRYPTO_SECRET_KEY = os.environ.get("CRYPTO_SECRET_KEY")

INVESTMENT_INCREMENTS = 5.0
MAX_COINS = 2

logging.basicConfig(level=logging.INFO)
app = Chalice(app_name="investorbot")

repo = CryptoRepo(CRYPTO_KEY, CRYPTO_SECRET_KEY)
dynamodb = boto3.resource("dynamodb", endpoint_url="http://dynamodb-local:8000")
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

    for order in repo.place_coin_orders(coin_selection):
        response = order_table.put_item(Item=order.__dict__)

    return coin_selection


# TODO REFACTOR THIS METHOD - this has been hacked together.
def sell_coin_routine():
    response = order_table.scan()
    data = response["Items"]

    orders = [Order(**order_dict) for order_dict in data]

    for order in orders:
        detail = repo.user.get_order_detail(order.client_oid)
        order_current_value = -1.0

        coin_balance = repo.get_coin_balance(detail.fee_instrument_name)

        if float(coin_balance.quantity) < (
            float(detail.quantity) * 0.995
        ):  # 0.995 accounts for any fee deductions (hopefully).
            continue

        if float(coin_balance.quantity) >= (float(detail.quantity) * 0.995) and float(
            coin_balance.quantity
        ) < float(detail.quantity):
            order_current_value = float(coin_balance.market_value)
        else:
            order_current_value = float(coin_balance.market_value) * (
                float(detail.quantity) / float(coin_balance.quantity)
            )  # quantity ratio is to account for having a larger quantity of coins in my wallet

        percentage_diff = order_current_value / float(detail.order_value)

        if percentage_diff > 1.01:
            instrument = repo.get_instrument(
                detail.instrument_name
            )  #! TODO find a better way to store instrument data.
            remainder = float(coin_balance.quantity) % float(instrument.qty_tick_size)

            final_sell_quantity = (
                float(coin_balance.quantity) - remainder
            )  # remainder needs deducting because Crypto.com fees don't respect their own quantity tick size requirement.

            quantity_percentage = final_sell_quantity / float(
                coin_balance.quantity
            )  # used to adjust final sell price after negating the quantity remainder

            sell_price = (quantity_percentage * order_current_value) / (
                final_sell_quantity
            )  # sell price adjusted after negating quantity remainder.

            # string formatting removes any trailing zeros or dodgy rounding.
            final_sell_quantity_string = f"{final_sell_quantity:g}"
            sell_price_string = f"{sell_price:g}"

            repo.user.create_order(
                detail.instrument_name,
                sell_price_string,
                final_sell_quantity_string,
                "SELL",
            )


@app.schedule(Rate(30, unit=Rate.MINUTES))
def buy_coin_routine_schedule(event):
    buy_coin_routine()


@app.schedule(Rate(15, unit=Rate.MINUTES))
def sell_coin_routine_schedule(event):
    sell_coin_routine()
