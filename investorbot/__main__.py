import argh
from investorbot.routines import (
    buy_coin_routine,
    sell_coin_routine,
    refresh_market_analysis_routine,
)
from investorbot.db import init_db

if __name__ == "__main__":
    argh.dispatch_commands(
        [
            init_db,
            buy_coin_routine,
            sell_coin_routine,
            refresh_market_analysis_routine,
        ]
    )
