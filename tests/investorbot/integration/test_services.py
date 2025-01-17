import json
import unittest
from unittest.mock import MagicMock, Mock, patch
import uuid

from investorbot import mappings
from investorbot.enums import TrendLineState
from investorbot.structs.ingress import InstrumentJson
from investorbot.services import AppService, CryptoService
from investorbot.models import (
    BuyOrder,
    CoinProperties,
    TimeSeriesMode,
    TimeSeriesSummary,
)

from tests.integration import get_mock_response


class TestAppService(unittest.TestCase):
    def setUp(self):
        instrument_data = None

        self.test_service = AppService("sqlite:///:memory:")
        self.test_service.run_migration()

        with open("./tests/integration/fixtures/get-instruments.json", "r") as f:
            instrument_data = json.loads(f.read())["result"]["data"]

        instruments = [InstrumentJson(**inst_data) for inst_data in instrument_data]
        coin_properties = [
            mappings.json_to_coin_properties(instrument) for instrument in instruments
        ]

        self.test_service.add_items(coin_properties)

    def test_get_buy_order_will_return_none_when_not_found(self):
        """Testing ORM will return None when buy orders do not exist."""
        result = self.test_service.get_buy_order("123")

        self.assertIsNone(result, "Buy order query result is not None.")

    def test_buy_order_can_be_stored_and_retrieved(self):
        """Testing my implementation of the ORM is able to add items and read said items from the
        app database."""
        buy_order_id = str(uuid.uuid4())

        buy_order = BuyOrder(
            buy_order_id=buy_order_id, coin_name="AGLD_USDT", price_per_coin=3.0
        )
        self.test_service.add_item(buy_order)

        db_buy_order = self.test_service.get_buy_order(buy_order_id)

        self.assertEqual(db_buy_order.buy_order_id, buy_order_id)
        self.assertIsInstance(
            db_buy_order.coin_properties.price_decimals,
            int,
            "Decimal place count must be an integer.",
        )
        self.assertIsInstance(
            db_buy_order.coin_properties.price_tick_size,
            float,
            "Tick size must be a float.",
        )
        self.assertIsInstance(
            db_buy_order.coin_properties.quantity_decimals,
            int,
            "Decimal value must be an integer.",
        )
        self.assertIsInstance(
            db_buy_order.coin_properties.quantity_tick_size,
            float,
            "Tick size must be a float.",
        )

    def test_time_series_summary_is_retrievable_with_modes(self):
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

        self.test_service.add_item(ts_summary)

        retrieved_ts_summary = self.test_service.get_time_series_with_coin_name(
            coin_name
        )

        count = len(retrieved_ts_summary)
        data = retrieved_ts_summary[0]

        self.assertTrue(count > 0, "Time series data was not returned.")
        self.assertIsNotNone(data.modes, "Modes were found to be None.")
        self.assertTrue(
            len(data.modes) == 3,
            "Number of modes doesn't match what was inserted into db.",
        )


@patch("investorbot.http.base.INVESTOR_APP_ENVIRONMENT", "Testing")
class TestCryptoService(unittest.TestCase):
    def setUp(self):
        self.test_crypto_service = CryptoService()
        self.test_crypto_service.user.api_key = "Test984bvwhibwbiytesTy"
        self.test_crypto_service.user.api_secret_key = "Test_ounghTtgwth874hWWWTESTG"

    @patch("investorbot.http.base.requests.post")
    def test_usd_balance_is_retrievable(self, mock_get: MagicMock):
        """Testing get_usd_balance correctly fetches my USD balance from the user balance JSON."""
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = get_mock_response(
            "private-user-balance-status-200"
        )

        usd_balance = self.test_crypto_service.get_usd_balance()

        self.assertAlmostEqual(6.221, usd_balance, 3)
