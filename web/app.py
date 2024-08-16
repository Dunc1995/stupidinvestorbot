import atexit
from flask import Flask, render_template
from investorbot import app_context
import investorbot.routines as routines
from flask_bootstrap import Bootstrap5
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
bootstrap = Bootstrap5(app)
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=routines.update_time_series_summaries_routine, trigger="interval", seconds=60
)
scheduler.start()


# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route("/time-series")
def time_series():
    ts_data = app_context.get_all_time_series_summaries()

    return render_template("time_series.html", time_series_data=ts_data)
