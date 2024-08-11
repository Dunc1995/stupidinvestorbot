import os
import sqlalchemy


CRYPTO_KEY = os.environ.get("CRYPTO_KEY")
CRYPTO_SECRET_KEY = os.environ.get("CRYPTO_SECRET_KEY")
CRYPTO_APP_ENVIRONMENT = os.environ.get("CRYPTO_APP_ENVIRONMENT")

INVESTMENT_INCREMENTS = 5
MAX_COINS = 4

engine = sqlalchemy.create_engine(
    "sqlite:////Users/duncanbailey/repos/stupidinvestorbot/db1.db"
)
