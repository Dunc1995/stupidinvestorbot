import argh
from investorbot.routines import (
    buy_coin_routine,
    sell_coin_routine,
    update_time_series_summaries_routine,
    init_db,
)
from investorbot.queries import show_time_series_summaries, show_time_series_summary_for

if __name__ == "__main__":
    argh.dispatch_commands(
        [
            buy_coin_routine,
            sell_coin_routine,
            update_time_series_summaries_routine,
            init_db,
            show_time_series_summaries,
            show_time_series_summary_for,
        ]
    )
