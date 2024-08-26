import argh
from investorbot.routines import (
    buy_coin_routine,
    cancel_orders_routine,
    get_market_analysis,
    sell_coin_routine,
    update_time_series_summaries_routine,
)
from investorbot.db import init_db

if __name__ == "__main__":
    argh.dispatch_commands(
        [
            init_db,
            cancel_orders_routine,
            buy_coin_routine,
            sell_coin_routine,
            get_market_analysis,
            update_time_series_summaries_routine,
        ]
    )
