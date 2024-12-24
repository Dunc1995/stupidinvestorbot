import atexit
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler


def placeholder() -> str:
    print("Hello world")


app = Flask(__name__)

scheduler = BackgroundScheduler()

scheduler.add_job(
    func=placeholder,
    trigger="interval",
    seconds=3,
    name="placeholder",
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
    return {"hello": "world"}


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
