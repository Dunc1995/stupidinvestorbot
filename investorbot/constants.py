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

CRYPTO_BASE_URL = "https://api.crypto.com/exchange/v1/"
CRYPTO_MARKET_URL = f"{CRYPTO_BASE_URL}public/"
CRYPTO_USER_URL = f"{CRYPTO_BASE_URL}private/"

CRYPTO_KEY = os.environ.get("CRYPTO_KEY")
CRYPTO_SECRET_KEY = os.environ.get("CRYPTO_SECRET_KEY")

DEFAULT_LOGS_NAME = "investor_bot_client"

# TODO Add this to CoinSelectionCriteria
INVESTMENT_INCREMENTS = 5.0
# TODO Add this to CoinSelectionCriteria
MAX_COINS = 4
