import atexit
from flask import Flask, json
from investorbot import app_service, crypto_service
import investorbot.routines as routines
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

scheduler = BackgroundScheduler()

# scheduler.add_job( func=routines.update_time_series_summaries_routine, trigger="interval",
#     minutes=60, name="update_time_series_summaries_routine", )
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
    orders = app_service.get_all_buy_orders()

    return [{"orderId": order.buy_order_id} for order in orders]
