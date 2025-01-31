from datetime import datetime
from investorbot.interfaces.providers import ITimeProvider


class TimeProvider(ITimeProvider):
    """User this time provider during live trading."""

    def now(self) -> datetime:
        return datetime.now()

    def now_in_ms(self) -> int:
        return int(datetime.now().timestamp()) * 1000
