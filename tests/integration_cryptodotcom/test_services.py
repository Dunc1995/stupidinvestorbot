import math
import uuid

from requests import Response

from investorbot.enums import TrendLineState
from investorbot.models import (
    BuyOrder,
    TimeSeriesMode,
    TimeSeriesSummary,
)


def test_get_buy_order_will_return_none_when_not_found(mock_bot_db):
    """Testing ORM will return None when buy orders do not exist."""
    result = mock_bot_db.get_buy_order("123")

    assert result is None, "Buy order query result is not None."


def test_buy_order_can_be_stored_and_retrieved(mock_bot_db):
    """Testing my implementation of the ORM is able to add items and read said items from the
    app database."""
    buy_order_id = str(uuid.uuid4())

    buy_order = BuyOrder(
        buy_order_id=buy_order_id, coin_name="AGLD_USDT", price_per_coin=3.0
    )
    mock_bot_db.add_item(buy_order)

    db_buy_order = mock_bot_db.get_buy_order(buy_order_id)

    assert db_buy_order.buy_order_id == buy_order_id

    assert isinstance(
        db_buy_order.coin_properties.price_decimals, int
    ), "Decimal place count must be an integer."

    assert isinstance(
        db_buy_order.coin_properties.price_decimals, int
    ), "Decimal place count must be an integer."
    assert isinstance(
        db_buy_order.coin_properties.price_tick_size, float
    ), "Tick size must be a float."
    assert isinstance(
        db_buy_order.coin_properties.quantity_decimals, int
    ), "Decimal value must be an integer."
    assert isinstance(
        db_buy_order.coin_properties.quantity_tick_size, float
    ), "Tick size must be a float."


def test_time_series_summary_is_retrievable_with_modes(mock_bot_db):
    """Ensuring ORM query is such that Modes are included in the time series data summary
    query."""
    coin_name = "TON_USD"

    ts_summary = TimeSeriesSummary(
        coin_name,
        12.0,
        0.5,
        12434134,
        0.001,
        11.0,
        0.0,
        0.0,
        0.0,
        21314314,
        120,
        [TimeSeriesMode(11.0), TimeSeriesMode(12.0), TimeSeriesMode(13.0)],
        TrendLineState.UNKNOWN,
    )

    ts_summary.market_analysis_id = -1

    mock_bot_db.add_item(ts_summary)

    retrieved_ts_summary = mock_bot_db.get_time_series_with_coin_name(coin_name)

    count = len(retrieved_ts_summary)
    data = retrieved_ts_summary[0]

    assert count > 0, "Time series data was not returned."
    assert data.modes is not None, "Modes were found to be None."
    assert (
        len(data.modes) == 3
    ), "Number of modes doesn't match what was inserted into db."


def test_usd_balance_is_retrievable(monkeypatch, mock_crypto_service, get_file_data):
    """Testing get_usd_balance correctly fetches my USD balance from the user balance JSON."""

    # Method that will replace the only network call made during this test.
    def mock_post_request(*args, **kwargs) -> dict:
        """Constructs the expected response inplace of the genuine POST request that would be made
        to the Crypto.com API."""
        response = Response()
        response.status_code = 200
        response.json = lambda: get_file_data("private-user-balance-status-200")

        return response

    # Ensure POST request is faked here.
    monkeypatch.setattr("requests.post", mock_post_request)

    # Expecting a single value to be retrieved from the private-user-balance-status-200 JSON.
    usd_balance = mock_crypto_service.get_usd_balance()

    assert math.isclose(6.221, usd_balance, rel_tol=1e-3)
