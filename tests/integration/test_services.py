import json
import unittest
from unittest.mock import MagicMock, Mock, patch
import uuid

from investorbot.integrations.cryptodotcom import mappings
from investorbot.enums import TrendLineState
from investorbot.integrations.cryptodotcom.structs import InstrumentJson
from investorbot.services import AppService
from investorbot.integrations.cryptodotcom.services import CryptoService
from investorbot.models import (
    BuyOrder,
    TimeSeriesMode,
    TimeSeriesSummary,
)

from tests.integration import get_mock_response


def test_get_buy_order_will_return_none_when_not_found(mock_app_service):
    """Testing ORM will return None when buy orders do not exist."""
    result = mock_app_service.get_buy_order("123")

    assert result is None, "Buy order query result is not None."


def test_buy_order_can_be_stored_and_retrieved(mock_app_service):
    """Testing my implementation of the ORM is able to add items and read said items from the
    app database."""
    buy_order_id = str(uuid.uuid4())

    buy_order = BuyOrder(
        buy_order_id=buy_order_id, coin_name="AGLD_USDT", price_per_coin=3.0
    )
    mock_app_service.add_item(buy_order)

    db_buy_order = mock_app_service.get_buy_order(buy_order_id)

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


def test_time_series_summary_is_retrievable_with_modes(mock_app_service):
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
        TrendLineState.UNKNOWN.value,
    )

    ts_summary.market_analysis_id = -1

    mock_app_service.add_item(ts_summary)

    retrieved_ts_summary = mock_app_service.get_time_series_with_coin_name(coin_name)

    count = len(retrieved_ts_summary)
    data = retrieved_ts_summary[0]

    assert count > 0, "Time series data was not returned."
    assert data.modes is not None, "Modes were found to be None."
    assert (
        len(data.modes) == 3
    ), "Number of modes doesn't match what was inserted into db."


class TestCryptoService(unittest.TestCase):
    def setUp(self):
        self.test_crypto_service = CryptoService()
        self.test_crypto_service.user.api_key = "Test984bvwhibwbiytesTy"
        self.test_crypto_service.user.api_secret_key = "Test_ounghTtgwth874hWWWTESTG"

    @patch("investorbot.integrations.cryptodotcom.http.base.requests.post")
    def test_usd_balance_is_retrievable(self, mock_get: MagicMock):
        """Testing get_usd_balance correctly fetches my USD balance from the user balance JSON."""
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = get_mock_response(
            "private-user-balance-status-200"
        )

        usd_balance = self.test_crypto_service.get_usd_balance()

        self.assertAlmostEqual(6.221, usd_balance, 3)
