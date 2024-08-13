import argh
from investorbot.routines import (
    buy_coin_routine,
    sell_coin_routine,
    update_time_series_summaries_routine,
)
from investorbot.subroutines import init_db
from investorbot.queries import (
    show_time_series_summaries,
    show_time_series_summary_for,
    show_investable_coin_count,
)

if __name__ == "__main__":
    argh.dispatch_commands(
        [
            init_db,
            buy_coin_routine,
            sell_coin_routine,
            update_time_series_summaries_routine,
            show_investable_coin_count,
            show_time_series_summaries,
            show_time_series_summary_for,
        ]
    )
