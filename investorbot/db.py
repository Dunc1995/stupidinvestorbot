import logging

from investorbot import app_service, crypto_service
from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.enums import MarketCharacterization
from investorbot.models import CoinSelectionCriteria

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def init_db():
    app_service.run_migration()

    coin_properties = crypto_service.get_coin_properties()
    market_analysis_ratings = [
        CoinSelectionCriteria(
            rating_id=MarketCharacterization.RISING_RAPIDLY.value,
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
            rating_id=MarketCharacterization.RISING.value,
            rating_description="Moderate Confidence",
            rating_upper_threshold=0.02,
            rating_lower_threshold=0.002,
            trend_line_should_be_rising=True,
            coin_should_be_an_nominal=True,
            maximum_number_of_orders=2,
            minimum_order_value_usd=20.0,
        ),
        CoinSelectionCriteria(
            rating_id=MarketCharacterization.FLAT.value,
            rating_description="Unsure",
            rating_upper_threshold=0.002,
            rating_lower_threshold=-0.002,
            trend_line_should_be_flat_or_rising=True,
            coin_should_be_an_nominal=True,
            coin_should_be_volatile=True,
            maximum_number_of_orders=3,
            minimum_order_value_usd=15.0,
        ),
        CoinSelectionCriteria(
            rating_id=MarketCharacterization.FALLING.value,
            rating_description="Low Confidence",
            rating_upper_threshold=-0.002,
            rating_lower_threshold=-0.02,
            coin_should_be_an_nominal=True,
            maximum_number_of_orders=4,
            minimum_order_value_usd=10.0,
        ),
        CoinSelectionCriteria(
            rating_id=MarketCharacterization.FALLING_RAPIDLY.value,
            rating_description="Very Low Confidence",
            rating_upper_threshold=-0.02,
            rating_lower_threshold=-1.0,
            rating_lower_unbounded=True,
            coin_should_be_an_nominal=True,
            maximum_number_of_orders=5,
            minimum_order_value_usd=5.0,
        ),
    ]

    app_service.add_items(coin_properties)
    app_service.add_items(market_analysis_ratings)
