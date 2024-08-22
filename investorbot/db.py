import logging

from investorbot import app_context, crypto_context
from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.models import MarketConfidenceRating

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def init_db():
    app_context.run_migration()

    coin_properties = crypto_context.get_coin_properties()
    market_confidence_ratings = [
        MarketConfidenceRating(1, "Very Confident"),
        MarketConfidenceRating(2, "Somewhat Confident"),
        MarketConfidenceRating(3, "Unsure"),
        MarketConfidenceRating(4, "Not Confident"),
        MarketConfidenceRating(5, "Do not Invest"),
    ]

    app_context.add_items(coin_properties)
    app_context.add_items(market_confidence_ratings)
