import atexit
from datetime import datetime, timedelta
from flask import Flask, abort, render_template, request
from investorbot.db import init_db
from investorbot.integrations.simulation import data_provider
from investorbot import is_crypto_dot_com, routines
from investorbot import crypto_service, app_service, is_simulation, smtp_service
from apscheduler.schedulers.background import BackgroundScheduler

from investorbot.models import CashBalance

# from investorbot.smtp import send_test_email

app = Flask(__name__)


def placeholder():
    print("HELLO")


def run_api(host="127.0.0.1", port=5000, persist_data=False):
    if not persist_data:
        init_db()

    scheduler = BackgroundScheduler()

    # scheduler.add_job( func=routines.update_time_series_summaries_routine, trigger="interval",
    #     minutes=60, name="update_time_series_summaries_routine", )
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
    return crypto_service.get_latest_trades()


@app.route("/get-valuation")
def get_valuation():
    coin_name = request.args.get("coin_name")

    if coin_name is None or "_USD" not in coin_name:
        return abort(404)

    return crypto_service.get_coin_time_series_data(coin_name)


@app.route("/get-market-analysis")
def get_market_analysis():
    analysis = app_service.get_market_analysis()[0]

    if analysis is None:
        return abort(404)

    return {
        "market_analysis": analysis.as_dict(),
        "time_series_statistics": [ts_data.as_dict() for ts_data in analysis.ts_data],
    }


@app.route("/get-orders")
def get_orders():
    orders = app_service.get_all_buy_orders()

    buy_orders = [order.as_dict() for order in orders]

    return buy_orders


@app.route("/get-balance-history")
def get_balance_history():
    balance_history = app_service.get_all_items(CashBalance)

    balances = [balance.as_dict() for balance in balance_history]

    return balances
