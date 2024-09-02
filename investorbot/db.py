import logging

from investorbot import app_service, crypto_service
from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.enums import ConfidenceRating
from investorbot.models import CoinSelectionCriteria

logger = logging.getLogger(DEFAULT_LOGS_NAME)


HIGH_CONFIDENCE = {
    "rating_id": ConfidenceRating.HIGH_CONFIDENCE.value,
    "rating_description": "High Confidence",
    "rating_upper_threshold": -1.0,
    "rating_upper_unbounded": True,
    "rating_lower_threshold": 0.02,
    "rating_lower_unbounded": False,
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
    "rating_id": ConfidenceRating.MODERATE_CONFIDENCE.value,
    "rating_description": "Moderate Confidence",
    "rating_upper_threshold": 0.02,
    "rating_upper_unbounded": False,
    "rating_lower_threshold": 0.002,
    "rating_lower_unbounded": False,
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
    "rating_id": ConfidenceRating.UNDECIDED.value,
    "rating_description": "Unsure",
    "rating_upper_threshold": 0.002,
    "rating_upper_unbounded": False,
    "rating_lower_threshold": -0.002,
    "rating_lower_unbounded": False,
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
    "rating_id": ConfidenceRating.LITTLE_CONFIDENCE.value,
    "rating_description": "Low Confidence",
    "rating_upper_threshold": -0.002,
    "rating_upper_unbounded": False,
    "rating_lower_threshold": -0.02,
    "rating_lower_unbounded": False,
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
    "rating_id": ConfidenceRating.NO_CONFIDENCE.value,
    "rating_description": "No Confidence - Do not Invest",
    "rating_upper_threshold": -0.02,
    "rating_upper_unbounded": False,
    "rating_lower_threshold": -1.0,
    "rating_lower_unbounded": True,
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
    app_service.run_migration()

    coin_properties = crypto_service.get_coin_properties()
    market_analysis_ratings = [
        CoinSelectionCriteria(**HIGH_CONFIDENCE),
        CoinSelectionCriteria(**MODERATE_CONFIDENCE),
        CoinSelectionCriteria(**UNDECIDED),
        CoinSelectionCriteria(**LITTLE_CONFIDENCE),
        CoinSelectionCriteria(**NO_CONFIDENCE),
    ]

    app_service.add_items(coin_properties)
    app_service.add_items(market_analysis_ratings)
