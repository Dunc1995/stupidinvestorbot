import json
from investorbot import app_context


# TODO could probably get this to show something more informative.
def show_investable_coin_count():
    coin_count = app_context.get_investable_coin_count()

    print(coin_count)


def show_time_series_summaries():
    ts_data = app_context.get_all_time_series_summaries()

    print(
        json.dumps(
            [ts.__dict__ for ts in ts_data],
            indent=4,
            default=lambda o: "<not serializable>",
        )
    )


def show_time_series_summary_for(coin_name: str):
    ts_data = app_context.get_time_series_with_coin_name(coin_name)

    print(
        json.dumps(
            [ts.__dict__ for ts in ts_data],
            indent=4,
            default=lambda o: "<not serializable>",
        )
    )
