import atexit
from flask import Flask, json, render_template
from investorbot import app_service, crypto_service
import investorbot.routines as routines
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

scheduler = BackgroundScheduler()


def placeholder():
    print("HELLO")


# scheduler.add_job( func=routines.update_time_series_summaries_routine, trigger="interval",
#     minutes=60, name="update_time_series_summaries_routine", )
scheduler.add_job(
    func=placeholder,
    trigger="interval",
    minutes=3,
    name="buy_coin_routine",
)
scheduler.add_job(
    func=placeholder,
    trigger="interval",
    minutes=3,
    name="sell_coin_routine",
)
scheduler.start()


# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route("/")
def index():
    # return {"latest-trades": "http://127.0.0.1:5000/get-latest-trades"}
    internal_links = ["/get-latest-trades"]
    crypto_dot_com_links = ["/get-tickers"]

    return render_template(
        "index.html",
        internal_links=internal_links,
        api_links=crypto_dot_com_links,
    )


@app.route("/get-latest-trades")
def get_latest_trades():
    return crypto_service.get_latest_trades()


@app.route("/get-tickers")
def get_tickers():
    return crypto_service.market.get_usd_tickers()
