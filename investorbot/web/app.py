from flask import Flask, render_template
from investorbot import app_context

app = Flask(__name__)


@app.route("/time-series")
def time_series():
    ts_data = app_context.get_all_time_series_summaries()

    return render_template("time_series.html", time_series_data=ts_data)
