import argh
from investorbot import is_simulation, smtp_service, crypto_service
from investorbot.routines import (
    get_coins_to_purchase,
    buy_coin_routine,
    sell_coin_routine,
    refresh_market_analysis_routine,
)
from investorbot.app import run_api
from investorbot.db import init_db
from investorbot.websocket import send_message
from investorbot.integrations.simulation import data_provider

if __name__ == "__main__":
    commands = [
        get_coins_to_purchase,
        buy_coin_routine,
        sell_coin_routine,
        refresh_market_analysis_routine,
        smtp_service.send_heartbeat,
        send_message,
        run_api,
        crypto_service.get_coin_time_series_data,
        data_provider.generate_time_series_data,
    ]

    if not is_simulation():
        commands.append(init_db)

    argh.dispatch_commands(commands)
