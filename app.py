import logging
import math
import os
from chalice import Chalice, Rate
import boto3
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

    user_balance = repo.get_wallet_balance()

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


def check_order_routine():
    response = order_table.scan()
    data = response["Items"]

    return data


@app.route("/")
def index():
    response = buy_coin_routine()

    return str(response)


@app.route("/check-orders")
def check_orders():
    response = check_order_routine()

    return str(response)


@app.schedule(Rate(1, unit=Rate.MINUTES))
def coin_check_routine(event):
    buy_coin_routine()
