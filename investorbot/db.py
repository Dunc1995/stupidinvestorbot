import logging
from os import path
import os

from investorbot.context import bot_context
from investorbot.constants import (
    DEFAULT_LOGS_NAME,
    INVESTOR_APP_DB_PATH,
)
from investorbot.enums import MarketCharacterization
from investorbot.env import is_simulation
from investorbot.integrations.simulation.constants import SIMULATION_DB_PATH
from investorbot.integrations.simulation.db import init_simulation_db
from investorbot.models import CoinSelectionCriteria

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def delete_file_if_exists(file_path: str):
    if path.exists(file_path):
        os.remove(file_path)
        logger.info(f"Deleted '{file_path}'")


def get_market_analysis_ratings():
    return [
        CoinSelectionCriteria(
            rating_id=MarketCharacterization.RISING_RAPIDLY,
            rating_description="High Confidence",
            rating_upper_threshold=-1.0,
            rating_upper_unbounded=True,
            rating_lower_threshold=0.02,
            coin_should_be_an_outlier=True,
            trend_line_should_be_rising=True,
            maximum_number_of_orders=1,
            minimum_order_value_usd=25.0,
        ),
        CoinSelectionCriteria(
            rating_id=MarketCharacterization.RISING,
            rating_description="Moderate Confidence",
            rating_upper_threshold=0.02,
            rating_lower_threshold=0.002,
            trend_line_should_be_rising=True,
            coin_should_be_nominal=True,
            maximum_number_of_orders=2,
            minimum_order_value_usd=20.0,
        ),
        CoinSelectionCriteria(
            rating_id=MarketCharacterization.FLAT,
            rating_description="Unsure",
            rating_upper_threshold=0.002,
            rating_lower_threshold=-0.002,
            trend_line_should_be_flat=True,
            trend_line_should_be_rising=True,
            coin_should_be_nominal=True,
            coin_should_be_volatile=True,
            maximum_number_of_orders=3,
            minimum_order_value_usd=15.0,
        ),
        CoinSelectionCriteria(
            rating_id=MarketCharacterization.FALLING,
            rating_description="Low Confidence",
            rating_upper_threshold=-0.002,
            rating_lower_threshold=-0.02,
            coin_should_be_nominal=True,
            maximum_number_of_orders=4,
            minimum_order_value_usd=10.0,
        ),
        CoinSelectionCriteria(
            rating_id=MarketCharacterization.FALLING_RAPIDLY,
            rating_description="Very Low Confidence",
            rating_upper_threshold=-0.02,
            rating_lower_threshold=-1.0,
            rating_lower_unbounded=True,
            coin_should_be_nominal=True,
            maximum_number_of_orders=5,
            minimum_order_value_usd=5.0,
        ),
    ]


def init_db():
    app_service = bot_context.db_service
    crypto_service = bot_context.crypto_service

    delete_file_if_exists(INVESTOR_APP_DB_PATH)
    logger.info("Running migration for app service.")
    app_service.run_migration()

    if is_simulation():
        delete_file_if_exists(SIMULATION_DB_PATH)
        logger.info("Running migration for simulation service.")
        init_simulation_db()

    coin_properties = crypto_service.get_coin_properties()
    market_analysis_ratings = get_market_analysis_ratings()

    app_service.add_items(coin_properties)
    app_service.add_items(market_analysis_ratings)
    logger.info("Initialization complete!")
