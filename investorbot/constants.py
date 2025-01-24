import os

INVESTOR_APP_ENVIRONMENT = os.environ.get("INVESTOR_APP_ENVIRONMENT")
INVESTOR_APP_PATH = os.environ.get("INVESTOR_APP_PATH")
INVESTOR_APP_FLATNESS_THRESHOLD = float(
    os.environ.get("INVESTOR_APP_FLATNESS_THRESHOLD")
    if os.environ.get("INVESTOR_APP_FLATNESS_THRESHOLD") is not None
    else 0.01
)
INVESTOR_APP_VOLATILITY_THRESHOLD = float(
    os.environ.get("INVESTOR_APP_VOLATILITY_THRESHOLD")
    if os.environ.get("INVESTOR_APP_VOLATILITY_THRESHOLD") is not None
    else 0.03
)
INVESTOR_APP_DB_CONNECTION = f"sqlite:///{INVESTOR_APP_PATH}app.db"

DEFAULT_LOGS_NAME = "investor_bot_client"

# TODO Add this to CoinSelectionCriteria
INVESTMENT_INCREMENTS = 10.0
MAX_COINS = 4

# SMTP
JINJA_ROOT_PATH = path = os.path.join(os.path.dirname(__file__), "templates")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")
