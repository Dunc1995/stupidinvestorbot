import logging

from investorbot import app_context, crypto_context
from investorbot.constants import DEFAULT_LOGS_NAME

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def init_db():
    app_context.run_migration()

    coin_properties = crypto_context.get_coin_properties()

    app_context.add_items(coin_properties)
