import sqlalchemy

from investorbot.repo import CryptoRepo, InvestorBotRepo

engine = sqlalchemy.create_engine(
    "sqlite:////Users/duncanbailey/repos/stupidinvestorbot/db1.db"
)

repo = CryptoRepo()
app_context = InvestorBotRepo()
