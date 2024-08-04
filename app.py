from decimal import Decimal
from chalice import Chalice, Rate
import boto3
from trade.state import TradeState
import uuid

app = Chalice(app_name="investorbot")


def check_coins(event):
    dynamodb = boto3.resource("dynamodb", endpoint_url="http://dynamodb-local:8000")
    table = dynamodb.Table("TradeStates")

    response = table.put_item(
        Item=TradeState(
            str(uuid.uuid4()), False, False, Decimal(1.0), Decimal(1.0), False, False
        ).__dict__
    )

    return response


@app.route("/")
def index():

    response = check_coins("testing")

    return print(response)


@app.schedule(Rate(1, unit=Rate.MINUTES))
def coin_check_routine(event):
    check_coins(event)


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
