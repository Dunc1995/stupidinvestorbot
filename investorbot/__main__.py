import argh
from investorbot import smtp_service
from investorbot.routines import (
    get_coins_to_purchase,
    buy_coin_routine,
    sell_coin_routine,
    refresh_market_analysis_routine,
)
from investorbot.app import run_api
from investorbot.db import init_db
from investorbot.websocket import send_message


if __name__ == "__main__":
    argh.dispatch_commands(
        [
            init_db,
            get_coins_to_purchase,
            buy_coin_routine,
            sell_coin_routine,
            refresh_market_analysis_routine,
            smtp_service.send_heartbeat,
            send_message,
            run_api,
        ]
    )
