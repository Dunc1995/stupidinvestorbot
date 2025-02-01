from datetime import datetime, timedelta
from investorbot.interfaces.providers import ITimeProvider


class TimeProvider(ITimeProvider):
    """Use this time provider when interacting with real API's."""

    def now(self) -> datetime:
        return datetime.now()

    def now_in_ms(self) -> int:
        return int(datetime.now().timestamp()) * 1000


class StaticTimeProvider(ITimeProvider):
    """This ITimeProvider should be used for testing purposes only. Simulates the passage of time by
    incrementing by 1 minute every time self.now() is called. This is to be used whenever the point
    in time is mostly irrelevant or in simplistic tests."""

    __current_time: datetime

    def __init__(self):
        self.__current_time = datetime.now()

    def now(self) -> datetime:
        self.__current_time += timedelta(minutes=1)

        return self.__current_time

    def now_in_ms(self) -> int:
        return int(self.__current_time.timestamp()) * 1000
