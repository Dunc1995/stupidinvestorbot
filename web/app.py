import atexit
from flask import Flask, render_template
from investorbot import app_context, crypto_context
import investorbot.routines as routines
from flask_bootstrap import Bootstrap5
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
bootstrap = Bootstrap5(app)
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=routines.cancel_orders_routine,
    trigger="interval",
    minutes=15,
    name="cancel_orders_routine",
)
scheduler.add_job(
    func=routines.update_time_series_summaries_routine,
    trigger="interval",
    minutes=60,
    name="update_time_series_summaries_routine",
)
scheduler.add_job(
    func=routines.buy_coin_routine,
    trigger="interval",
    minutes=3,
    name="buy_coin_routine",
)
scheduler.add_job(
    func=routines.sell_coin_routine,
    trigger="interval",
    minutes=3,
    name="sell_coin_routine",
)
scheduler.start()


# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route("/")
def home():
    order_details = []
    orders = app_context.get_all_buy_orders()

    for order in orders:
        order_detail = crypto_context.get_order_detail(order.buy_order_id)
        order_details.append(order_detail)

    return render_template("home.html", order_details=order_details)


@app.route("/time-series")
def time_series():
    ts_data = app_context.get_all_time_series_summaries()

    return render_template("time_series.html", time_series_data=ts_data)
