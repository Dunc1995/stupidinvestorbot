import atexit
from flask import Flask, request, jsonify

from apscheduler.schedulers.background import BackgroundScheduler
from marketsimulator import market_simulator_service
from marketsimulator.db import add_ts_data


app = Flask(__name__)

scheduler = BackgroundScheduler()

scheduler.add_job(
    func=add_ts_data,
    trigger="interval",
    seconds=5,
    name="add_ts_data",
)
scheduler.start()


# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route("/")
def home():
    return {"hello": "world"}


@app.route("/public/get-tickers")
def get_tickers():
    return {"hello": "world"}


@app.route("/public/get-instruments")
def get_instruments():
    return {"hello": "world"}


@app.route("/public/get-valuations")
def get_valuations():
    instrument_name = request.args.get("instrument_name")

    valuation = market_simulator_service.get_valuation(instrument_name)

    print(valuation)

    response = jsonify(
        {
            "id": -1,
            "method": "public/get-valuations",
            "code": 0,
            "result": {
                "data": (
                    [value.to_dict() for value in valuation.valuation]
                    if valuation is not None
                    else []
                ),
                "instrument_name": instrument_name,
            },
        }
    )

    response.headers.add("Access-Control-Allow-Origin", "*")

    return response


@app.route("/private/user_balance")
def user_balance():
    return {"hello": "world"}


@app.route("/private/create-order")
def create_order():
    return {"hello": "world"}


@app.route("/private/cancel-order")
def cancel_order():
    return {"hello": "world"}


@app.route("/private/get-order-detail")
def get_order_detail():
    return {"hello": "world"}
