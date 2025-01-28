import os


CRYPTO_BASE_URL = "https://api.crypto.com/exchange/v1/"
CRYPTO_MARKET_URL = f"{CRYPTO_BASE_URL}public/"
CRYPTO_USER_URL = f"{CRYPTO_BASE_URL}private/"

CRYPTO_KEY = os.environ.get("CRYPTO_KEY")
CRYPTO_SECRET_KEY = os.environ.get("CRYPTO_SECRET_KEY")
