from typing import List
import sqlalchemy
from sqlalchemy import Engine
from sqlalchemy.orm import Session, joinedload

from marketsimulator.constants import MARKET_SIMULATOR_APP_DB_CONNECTION
from marketsimulator.models import Base, Instrument


class MarketSimulatorService:
    __engine: Engine

    def __init__(self, connection_string=MARKET_SIMULATOR_APP_DB_CONNECTION):
        self.__engine = sqlalchemy.create_engine(
            connection_string, pool_size=40, max_overflow=0
        )

    @property
    def session(self) -> Session:
        return Session(self.__engine)

    def run_migration(self):
        Base.metadata.create_all(self.__engine)

    def add_item(self, db_object: Base):
        with self.session as session:
            session.add(db_object)
            session.commit()

    def add_items(self, db_objects: List[Base]):
        with self.session as session:
            session.add_all(db_objects)
            session.commit()

    def get_all_items(self, type: Base) -> List[Base]:
        items_list = []
        session = self.session

        query = sqlalchemy.select(type)
        for item in session.scalars(query):
            items_list.append(item)

        return items_list

    def get_valuation(self, coin_name: str) -> Instrument:
        session = self.session

        query = (
            sqlalchemy.select(Instrument)
            .where(Instrument.symbol == coin_name)
            .options(joinedload(Instrument.valuation))
        )

        return session.scalar(query)
