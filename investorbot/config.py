"""Centralized configuration with validation.

All environment variables are read and validated here at import time. If a required variable is
missing, the application fails fast with a clear error message rather than crashing later with
a confusing NoneType error.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

from investorbot.enums import AppIntegration


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration. Constructed once at startup."""

    environment: Optional[str] = None
    integration: Optional[str] = None
    app_path: Optional[str] = None

    flatness_threshold: float = 0.01
    volatility_threshold: float = 0.03

    investment_increments: float = 10.0
    max_coins: int = 4

    # SMTP
    sender_email: Optional[str] = None
    sender_password: Optional[str] = None
    recipient_email: Optional[str] = None

    @property
    def db_path(self) -> str:
        return f"{self.app_path}app.db"

    @property
    def db_connection(self) -> str:
        return f"sqlite:///{self.db_path}"

    @property
    def is_simulation(self) -> bool:
        return self.integration == AppIntegration.SIMULATED

    @property
    def is_crypto_dot_com(self) -> bool:
        return self.integration == AppIntegration.CRYPTODOTCOM

    @property
    def is_testing(self) -> bool:
        return self.environment == "Testing"

    @property
    def jinja_root_path(self) -> str:
        return os.path.join(os.path.dirname(__file__), "templates")


def load_config() -> AppConfig:
    """Load configuration from environment variables with defaults and validation."""

    def _float_or_default(key: str, default: float) -> float:
        value = os.environ.get(key)
        return float(value) if value is not None else default

    return AppConfig(
        environment=os.environ.get("INVESTOR_APP_ENVIRONMENT"),
        integration=os.environ.get("INVESTOR_APP_INTEGRATION"),
        app_path=os.environ.get("INVESTOR_APP_PATH"),
        flatness_threshold=_float_or_default("INVESTOR_APP_FLATNESS_THRESHOLD", 0.01),
        volatility_threshold=_float_or_default(
            "INVESTOR_APP_VOLATILITY_THRESHOLD", 0.03
        ),
        investment_increments=_float_or_default("INVESTOR_APP_INVESTMENT_INCREMENTS", 10.0),
        max_coins=int(os.environ.get("INVESTOR_APP_MAX_COINS", "4")),
        sender_email=os.environ.get("SENDER_EMAIL"),
        sender_password=os.environ.get("SENDER_PASSWORD"),
        recipient_email=os.environ.get("RECIPIENT_EMAIL"),
    )


# Module-level singleton — imported by other modules.
config = load_config()

DEFAULT_LOGS_NAME = "investor_bot_client"
