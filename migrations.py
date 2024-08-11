import sqlalchemy
from sqlalchemy.orm import Session
from investorbot import CRYPTO_KEY, CRYPTO_SECRET_KEY
from investorbot.repo import CryptoRepo
from investorbot.tables import Base, CoinProperties

repo = CryptoRepo(CRYPTO_KEY, CRYPTO_SECRET_KEY)

engine = sqlalchemy.create_engine(
    "sqlite:////Users/duncanbailey/repos/stupidinvestorbot/app.db"
)


if __name__ == "__main__":
    Base.metadata.create_all(engine)

    coin_properties = [
        CoinProperties(
            coin_name=instrument.symbol,
            quantity_tick_size=instrument.qty_tick_size,
            quantity_decimals=instrument.quantity_decimals,
            price_tick_size=instrument.price_tick_size,
            price_decimals=instrument.quote_decimals,
        )
        for instrument in repo.instruments
    ]

    with Session(engine) as session:
        session.add_all(coin_properties)
        session.commit()
