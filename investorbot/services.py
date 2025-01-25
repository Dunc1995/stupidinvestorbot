from datetime import datetime, timedelta
from email.mime.text import MIMEText
import logging
import smtplib
from typing import List, Tuple

from jinja2 import Environment, FileSystemLoader
import sqlalchemy
from sqlalchemy import Engine
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm import DeclarativeBase

from investorbot.integrations.cryptodotcom import mappings
from investorbot.constants import (
    DEFAULT_LOGS_NAME,
    JINJA_ROOT_PATH,
    RECIPIENT_EMAIL,
    SENDER_EMAIL,
    SENDER_PASSWORD,
)
from investorbot.structs.internal import (
    RatingThreshold,
)
from investorbot.models import (
    Base,
    BuyOrder,
    CoinProperties,
    CoinSelectionCriteria,
    MarketAnalysis,
    TimeSeriesSummary,
)
from investorbot.analysis import time_now, convert_ms_time_to_hours

logger = logging.getLogger(DEFAULT_LOGS_NAME)


class BaseAppService:
    __engine: Engine

    def __init__(self, base: DeclarativeBase, connection_string):
        self.__engine = sqlalchemy.create_engine(connection_string)
        self.__base = base

    @property
    def session(self) -> Session:
        return Session(self.__engine)

    def run_migration(self):
        self.__base.metadata.create_all(self.__engine)

    def add_item(self, db_object: DeclarativeBase):
        with self.session as session:
            session.add(db_object)
            session.commit()

    def add_items(self, db_objects: List[DeclarativeBase]):
        with self.session as session:
            session.add_all(db_objects)
            session.commit()

    def get_all_items(self, type: DeclarativeBase) -> List[DeclarativeBase]:
        items_list = []
        session = self.session

        query = sqlalchemy.select(type)
        for item in session.scalars(query):
            items_list.append(item)

        return items_list


class AppService(BaseAppService):
    def __init__(self, connection_string):
        super().__init__(Base, connection_string)

    def get_buy_order(self, buy_order_id: str) -> BuyOrder | None:
        session = self.session

        query = (
            sqlalchemy.select(BuyOrder)
            .where(BuyOrder.buy_order_id == buy_order_id)
            .options(joinedload(BuyOrder.sell_order))
        )

        return session.scalar(query)

    def get_all_buy_orders(self) -> List[BuyOrder]:
        items_list = []
        session = self.session

        query = (
            sqlalchemy.select(BuyOrder)
            .options(joinedload(BuyOrder.coin_properties))
            .options(joinedload(BuyOrder.sell_order))
        )

        for item in session.scalars(query):
            items_list.append(item)

        return items_list

    def delete_buy_order(self, buy_order_id: int):
        with self.session as session:
            item = (
                session.query(BuyOrder)
                .where(BuyOrder.buy_order_id == buy_order_id)
                .first()
            )

            session.delete(item)
            session.commit()

    def get_time_series_with_coin_name(
        self, coin_name: str
    ) -> List[TimeSeriesSummary] | None:
        ts_data = []
        session = self.session

        query = sqlalchemy.select(TimeSeriesSummary).where(
            TimeSeriesSummary.coin_name == coin_name
        )
        for item in session.scalars(query):
            ts_data.append(item)

        return ts_data

    def __get_market_analysis(self) -> MarketAnalysis | None:
        session = self.session

        latest_market_analysis = (
            session.query(MarketAnalysis)
            .options(
                joinedload(MarketAnalysis.ts_data).subqueryload(TimeSeriesSummary.modes)
            )
            .order_by(MarketAnalysis.market_analysis_id.desc())
            .first()
        )

        return latest_market_analysis

    def get_market_analysis(self) -> Tuple[MarketAnalysis, bool]:
        """If the latest time series data is older than an hour, then this method will return true
        in addition to the current market analysis."""

        market_analysis = self.__get_market_analysis()

        should_refresh_ts_data = (
            convert_ms_time_to_hours(time_now(), market_analysis.creation_time_ms)
            >= 1.0
        )

        return market_analysis, should_refresh_ts_data

    def delete_existing_time_series(self):
        with self.session as session:
            now = time_now()
            query = (
                session.query(MarketAnalysis)
                .options(
                    joinedload(MarketAnalysis.ts_data).subqueryload(
                        TimeSeriesSummary.modes
                    )
                )
                .where(MarketAnalysis.creation_time_ms < now)
            )

            for item in session.scalars(query):
                session.delete(item)

            session.commit()

    def get_coin_properties(self, coin_name: str) -> CoinProperties | None:
        session = self.session

        query = sqlalchemy.select(CoinProperties).where(
            CoinProperties.coin_name == coin_name
        )
        return session.scalar(query)

    def get_rating_thresholds(self) -> List[RatingThreshold]:
        coin_selection_criteria: List[CoinSelectionCriteria] = self.get_all_items(
            CoinSelectionCriteria
        )

        return [
            mappings.coin_selection_to_rating_threshold(criteria)
            for criteria in coin_selection_criteria
        ]

    def get_selection_criteria(self, selection_id: int) -> CoinSelectionCriteria | None:
        session = self.session

        query = sqlalchemy.select(CoinSelectionCriteria).where(
            CoinSelectionCriteria.rating_id == selection_id
        )

        return session.scalar(query)


class SmtpService:
    environment: Environment
    sender_email: str
    sender_password: str
    recipient_email: str
    start_time: datetime

    def __init__(
        self,
        sender_email=SENDER_EMAIL,
        sender_password=SENDER_PASSWORD,
        recipient_email=RECIPIENT_EMAIL,
        jinja_root_path=JINJA_ROOT_PATH,
    ):
        self.environment = Environment(loader=FileSystemLoader(jinja_root_path))
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        self.start_time = datetime.now()

    def get_template(self, template_name: str) -> str:
        return self.environment.get_template(f"emails/{template_name}.html")

    def send_email(self, subject: str, template_name: str, **kwargs):
        sender_email = self.sender_email
        sender_password = self.sender_password
        recipient_email = self.recipient_email
        template = self.get_template(template_name)

        content = template.render(**kwargs)

        html_message = MIMEText(content, "html")
        html_message["Subject"] = "Investor Bot - " + subject
        html_message["From"] = sender_email
        html_message["To"] = recipient_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, html_message.as_string())

    def send_test_email(self):
        self.send_email(subject="Test Email", template_name="example")

    def send_heartbeat(self):
        current_time: datetime = datetime.now()
        delta: timedelta = current_time - self.start_time

        interval_seconds = delta.total_seconds()
        interval_minutes = round(interval_seconds / 60)

        unit = "minute" if interval_minutes == 1 else "minutes"
        uptime = f"{interval_minutes} {unit}"

        self.send_email(
            subject="Heartbeat",
            template_name="heartbeat",
            start_time=self.start_time,
            uptime=uptime,
        )
