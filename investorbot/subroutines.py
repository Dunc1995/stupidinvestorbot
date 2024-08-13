import json
import logging
from typing import Any, Generator, Tuple

from investorbot import app_context, crypto_context
from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.models import TimeSeriesSummary
from investorbot.structs.internal import LatestTrade

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def init_db():
    app_context.run_migration()

    coin_properties = crypto_context.get_coin_properties()

    app_context.add_items(coin_properties)


def get_latest_trade_stats() -> (
    Generator[Tuple[LatestTrade, TimeSeriesSummary], Any, None]
):
    """Fetches latest trades corresponding to cached time series stats.

    Yields: Generator[Tuple[LatestTrade, TimeSeriesSummary], Any, None]:
        Yielding here is really important for minimising latency between running analysis
        and purchasing a coin - latency will invalidate the analysis and attempted coin
        purchase if this script is too slow in placing buy orders.
    """
    ts_summaries = app_context.get_all_time_series_summaries()

    for ts_summary in ts_summaries:
        latest_trade = crypto_context.get_latest_trade(ts_summary.coin_name)

        logger.info(
            json.dumps(
                {
                    "latest_trade": latest_trade.__dict__,
                    "time_series_stats": ts_summary.__dict__,
                },
                indent=4,
                default=lambda o: "<not serializable>",
            )
        )

        yield latest_trade, ts_summary
