import atexit
from datetime import datetime, timedelta
from flask import Flask, render_template, request
from investorbot.db import init_db
from investorbot.integrations.simulation import data_provider
from investorbot import routines
from investorbot import crypto_service, is_simulation, smtp_service
from apscheduler.schedulers.background import BackgroundScheduler

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

    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

    app.run(host, port)


@app.route("/")
def index():
    # return {"latest-trades": "http://127.0.0.1:5000/get-latest-trades"}
    crypto_dot_com_links = [
        "/get-tickers",
        "/get-valuations?instrument_name=BTC_USD&valuation_type=mark_price&count=2880",
        "/user-balance",
    ]
    internal_links = [
        {
            "link": "/get-latest-trades",
            "description": "derived from '/get-tickers'",
        }
    ]
    functionality_links = [
        {
            "link": "/test-smtp",
            "description": "sends a test email to bot owner.",
        },
    ]

    return render_template(
        "index.html",
        internal_links=internal_links,
        api_links=crypto_dot_com_links,
        functionality_links=functionality_links,
    )


@app.route("/get-tickers")
def get_tickers():
    return crypto_service.market.get_usd_tickers()


@app.route("/get-valuations")
def get_valuations():
    instrument_name = request.args.get("instrument_name")
    valuation_type = request.args.get("valuation_type")

    return crypto_service.market.get_valuation(instrument_name, valuation_type)


@app.route("/user-balance")
def get_user_balance():
    return crypto_service.user.get_balance().__dict__


@app.route("/get-latest-trades")
def get_latest_trades():
    return crypto_service.get_latest_trades()


@app.route("/test-smtp")
def send_test_email_link():
    smtp_service.send_test_email()

    return {"message": "email sent"}
