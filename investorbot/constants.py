"""Backward-compatible constants module.

All configuration now lives in investorbot.config. This module re-exports values so existing
imports continue to work during the migration.
"""

from investorbot.config import config, DEFAULT_LOGS_NAME  # noqa: F401

# Re-export config values as module-level constants for backward compatibility.
INVESTOR_APP_ENVIRONMENT = config.environment
INVESTOR_APP_INTEGRATION = config.integration
INVESTOR_APP_PATH = config.app_path
INVESTOR_APP_FLATNESS_THRESHOLD = config.flatness_threshold
INVESTOR_APP_VOLATILITY_THRESHOLD = config.volatility_threshold
INVESTOR_APP_DB_PATH = config.db_path if config.app_path else f"{config.app_path}app.db"
INVESTOR_APP_DB_CONNECTION = config.db_connection if config.app_path else f"sqlite:///{config.app_path}app.db"

INVESTMENT_INCREMENTS = config.investment_increments
MAX_COINS = config.max_coins

# SMTP
JINJA_ROOT_PATH = config.jinja_root_path
SENDER_EMAIL = config.sender_email
SENDER_PASSWORD = config.sender_password
RECIPIENT_EMAIL = config.recipient_email
