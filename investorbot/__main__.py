import logging
import argh
from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.routines import (
    get_coins_to_purchase,
    buy_coin_routine,
    sell_coin_routine,
    refresh_market_analysis_routine,
)
from investorbot.app import run_api
from investorbot.env import is_simulation
from investorbot.context import bot_context
from investorbot.db import init_db
from investorbot.websocket import track_ticker

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def main():
    try:
        commands = [
            get_coins_to_purchase,
            buy_coin_routine,
            sell_coin_routine,
            refresh_market_analysis_routine,
            bot_context.smtp_service.send_heartbeat,
            run_api,
            bot_context.crypto_service.get_coin_time_series_data,
            track_ticker,
        ]

        if not is_simulation():
            commands.append(init_db)

        argh.dispatch_commands(commands)
    except EnvironmentError as e:
        logger.fatal(e)


if __name__ == "__main__":
    main()
