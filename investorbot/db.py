import logging

from investorbot import app_context, crypto_context
from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.models import CoinSelectionCriteria

logger = logging.getLogger(DEFAULT_LOGS_NAME)


HIGH_CONFIDENCE = {
    "rating_id": 1,
    "rating_description": "High Confidence",
    "trade_needs_to_be_within_mean_and_upper_bound": False,
    "trade_needs_to_be_within_mean_and_lower_bound": True,
    "standard_deviation_threshold_should_exceed_threshold": True,
    "standard_deviation_threshold": 0.03,
    "trend_line_percentage_threshold": 0.005,
    "trend_line_should_be_flat": False,
    "trend_line_should_be_rising": True,
    "trend_line_should_be_falling": False,
    "trend_line_should_be_flat_or_rising": False,
}

MODERATE_CONFIDENCE = {
    "rating_id": 2,
    "rating_description": "Moderate Confidence",
    "trade_needs_to_be_within_mean_and_upper_bound": False,
    "trade_needs_to_be_within_mean_and_lower_bound": True,
    "standard_deviation_threshold_should_exceed_threshold": True,
    "standard_deviation_threshold": 0.025,
    "trend_line_percentage_threshold": 0.001,
    "trend_line_should_be_flat": False,
    "trend_line_should_be_rising": True,
    "trend_line_should_be_falling": False,
    "trend_line_should_be_flat_or_rising": False,
}

UNDECIDED = {
    "rating_id": 3,
    "rating_description": "Unsure",
    "trade_needs_to_be_within_mean_and_upper_bound": False,
    "trade_needs_to_be_within_mean_and_lower_bound": True,
    "standard_deviation_threshold_should_exceed_threshold": True,
    "standard_deviation_threshold": 0.02,
    "trend_line_percentage_threshold": 0.002,
    "trend_line_should_be_flat": False,
    "trend_line_should_be_rising": False,
    "trend_line_should_be_falling": False,
    "trend_line_should_be_flat_or_rising": True,
}

LITTLE_CONFIDENCE = {
    "rating_id": 4,
    "rating_description": "Low Confidence",
    "trade_needs_to_be_within_mean_and_upper_bound": False,
    "trade_needs_to_be_within_mean_and_lower_bound": True,
    "standard_deviation_threshold_should_exceed_threshold": True,
    "standard_deviation_threshold": 0.02,
    "trend_line_percentage_threshold": 0.005,
    "trend_line_should_be_flat": False,
    "trend_line_should_be_rising": False,
    "trend_line_should_be_falling": False,
    "trend_line_should_be_flat_or_rising": True,
}

NO_CONFIDENCE = {
    "rating_id": 5,
    "rating_description": "No Confidence - Do not Invest",
    "trade_needs_to_be_within_mean_and_upper_bound": False,
    "trade_needs_to_be_within_mean_and_lower_bound": False,
    "standard_deviation_threshold_should_exceed_threshold": False,
    "standard_deviation_threshold": 0.02,
    "trend_line_percentage_threshold": 0.005,
    "trend_line_should_be_flat": False,
    "trend_line_should_be_rising": False,
    "trend_line_should_be_falling": False,
    "trend_line_should_be_flat_or_rising": False,
}


def init_db():
    app_context.run_migration()

    coin_properties = crypto_context.get_coin_properties()
    market_analysis_ratings = [
        CoinSelectionCriteria(**HIGH_CONFIDENCE),
        CoinSelectionCriteria(**MODERATE_CONFIDENCE),
        CoinSelectionCriteria(**UNDECIDED),
        CoinSelectionCriteria(**LITTLE_CONFIDENCE),
        CoinSelectionCriteria(**NO_CONFIDENCE),
    ]

    app_context.add_items(coin_properties)
    app_context.add_items(market_analysis_ratings)
