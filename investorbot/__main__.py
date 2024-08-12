import argh
from investorbot.routines import (
    buy_coin_routine,
    sell_coin_routine,
    get_coin_data_routine,
    init_db,
)

if __name__ == "__main__":
    argh.dispatch_commands(
        [buy_coin_routine, sell_coin_routine, get_coin_data_routine, init_db]
    )
