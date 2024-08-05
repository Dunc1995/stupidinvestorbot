from decimal import Decimal
import os
from chalice import Chalice, Rate
import boto3
from chalicelib.repo import CryptoRepo
from chalicelib.strategies import CoinSelectionStrategies
from chalicelib.trade.state import TradeMetaData
import uuid

CRYPTO_KEY = os.environ.get("CRYPTO_KEY")
CRYPTO_SECRET_KEY = os.environ.get("CRYPTO_SECRET_KEY")

INVESTMENT_INCREMENTS = 50.0

repo = CryptoRepo(CRYPTO_KEY, CRYPTO_SECRET_KEY)
app = Chalice(app_name="investorbot")


def buy_coin_routine():
    # dynamodb = boto3.resource("dynamodb", endpoint_url="http://dynamodb-local:8000")
    # table = dynamodb.Table("TradeStates")

    # response = table.put_item(
    #     Item=TradeMetaData(
    #         str(uuid.uuid4()), False, False, Decimal(1.0), Decimal(1.0), False, False
    #     ).__dict__
    # )

    coin_selection = repo.select_coins_of_interest(CoinSelectionStrategies.HIGH_GAIN)

    # instrument = next(x for x in repo.instruments if x.symbol == coin.name)

    # ticker_data = repo.market.get_ticker(coin.name)
    # latest_trade = Decimal(ticker_data.latest_trade)

    # percentage_change = latest_trade / Decimal(str(coin.latest_trade))

    # if percentage_change > 1.01:
    #     print(
    #         f"Skipping purchase of {coin.name} as value has increased since initial analysis."
    #     )
    # else:
    #     coin.latest_trade = latest_trade

    #     order_summary = purchase_coin(coin, instrument, strategy)

    return [coin.__dict__ for coin in coin_selection]


@app.route("/user-balance")
def get_user_balance():
    return repo.user.get_balance()


@app.route("/get-usd-coins")
def get_usd_coins():
    return [ticker.__dict__ for ticker in repo.market.get_usd_coins()]


@app.route("/get-instruments")
def get_instruments():
    return [instrument.__dict__ for instrument in repo.market.get_instruments()]


@app.route("/")
def index():
    response = buy_coin_routine()
    return print(response)


@app.schedule(Rate(1, unit=Rate.MINUTES))
def coin_check_routine(event):
    buy_coin_routine()


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
