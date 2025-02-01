import atexit
from datetime import datetime, timedelta
from flask import Flask, abort, render_template, request
from flask_cors import CORS, cross_origin

from investorbot.context import bot_context
from investorbot.db import init_db
from investorbot.env import is_crypto_dot_com, is_simulation
from investorbot import routines
from apscheduler.schedulers.background import BackgroundScheduler

from investorbot.integrations.simulation.services import SimulatedCryptoService
from investorbot.models import CashBalance

# from investorbot.smtp import send_test_email

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5371"}})


def analysis_routine():
    return routines.refresh_market_analysis_routine(hours=24)


def run_api(host="127.0.0.1", port=5000, persist_data=False):
    smtp_service = bot_context.smtp_service
    data_provider = None

    if isinstance(bot_context.crypto_service, SimulatedCryptoService):
        data_provider = bot_context.crypto_service.data

    if not persist_data:
        init_db()

    scheduler = BackgroundScheduler()

    market_analysis_job = scheduler.add_job(
        func=analysis_routine,
        trigger="interval",
        minutes=15,
        name="refresh_market_analysis_routine",
    )

    market_analysis_job.modify(next_run_time=datetime.now() + timedelta(seconds=25))

    scheduler.add_job(
        func=smtp_service.send_heartbeat,
        trigger="interval",
        minutes=15,
        name="heartbeat",
    )

    buy_coin_job = scheduler.add_job(
        func=routines.buy_coin_routine,
        trigger="interval",
        seconds=20,
        name="buy_coin_routine",
    )

    buy_coin_job.modify(next_run_time=datetime.now() + timedelta(seconds=25))

    sell_coin_job = scheduler.add_job(
        func=routines.sell_coin_routine,
        trigger="interval",
        seconds=20,
        name="sell_coin_routine",
    )

    sell_coin_job.modify(next_run_time=datetime.now() + timedelta(seconds=35))

    if is_simulation():
        job = scheduler.add_job(
            func=data_provider.run_in_real_time,
            trigger="interval",
            minutes=60,
            name="simulation",
        )
        job.modify(next_run_time=datetime.now() + timedelta(seconds=5))

    if not is_crypto_dot_com():
        scheduler.start()

        # Shut down the scheduler when exiting the app
        atexit.register(lambda: scheduler.shutdown())

    app.run(host, port)


@app.route("/")
def index():
    internal_links = [
        {
            "link": "/get-latest-trades",
            "description": "derived from '/get-tickers'",
        },
        {
            "link": "/get-market-analysis",
            "description": "gets statistical summaries for coins of interest.",
        },
        {
            "link": "/get-valuation?coin_name=BTC_USD",
            "description": "get time series data for a particular coin.",
        },
        {
            "link": "/get-orders",
            "description": "get all orders.",
        },
        {
            "link": "/get-balance-history",
            "description": "show historical wallet value.",
        },
    ]

    return render_template("index.html", internal_links=internal_links)


@app.route("/get-latest-trades")
def get_latest_trades():
    return bot_context.crypto_service.get_latest_trades()


@app.route("/get-valuation")
@cross_origin()
def get_valuation():
    coin_name = request.args.get("coin_name")

    if coin_name is None or "_USD" not in coin_name:
        return abort(404)

    return bot_context.crypto_service.get_coin_time_series_data(coin_name)


@app.route("/get-market-analysis")
def get_market_analysis():
    analysis = bot_context.db_service.get_market_analysis()[0]

    if analysis is None:
        return abort(404)

    return {
        "market_analysis": analysis.as_dict(),
        "time_series_statistics": [ts_data.as_dict() for ts_data in analysis.ts_data],
    }


@app.route("/get-orders")
def get_orders():
    orders = bot_context.db_service.get_all_buy_orders()

    buy_orders = [order.as_dict() for order in orders]

    return buy_orders


@app.route("/get-balance-history")
def get_balance_history():
    balance_history = bot_context.db_service.get_all_items(CashBalance)

    balances = [balance.as_dict() for balance in balance_history]

    return balances
