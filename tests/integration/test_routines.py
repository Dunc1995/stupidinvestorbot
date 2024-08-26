import unittest
from unittest.mock import MagicMock, Mock, patch

from investorbot.contexts import AppContext
from investorbot.db import init_db, app_context
from investorbot.routines import buy_coin_routine, update_time_series_summaries_routine
from tests.integration import get_mock_response


class TestRoutines(unittest.TestCase):

    @patch("investorbot.http.base.requests.get")
    def setUp(self, mock_instruments: MagicMock):
        mock_instruments.return_value = Mock(ok=True)
        mock_instruments.return_value.json.return_value = get_mock_response(
            "get-instruments.json"
        )

        context = AppContext("sqlite:///:memory:")

        self.patcher_environment = patch(
            "investorbot.http.base.INVESTOR_APP_ENVIRONMENT", "Testing"
        )
        self.patcher_db_app_context = patch("investorbot.db.app_context", context)
        self.patcher_routine_app_context = patch(
            "investorbot.routines.app_context", context
        )

        self.mock_environment = self.patcher_environment.start()
        self.mock_db_context_db = self.patcher_db_app_context.start()
        self.mock_db_context_routines = self.patcher_routine_app_context.start()
        self.addCleanup(self.patcher_environment.stop)
        self.addCleanup(self.patcher_db_app_context.stop)
        self.addCleanup(self.patcher_routine_app_context.stop)

        init_db()

    # @patch("investorbot.crypto_context.get_usd_balance", return_value=27.65)
    # @patch("investorbot.crypto_context.get_investable_coin_count", return_value=5)
    # def test_usd_balance_is_retrievable(self, mock_coin_count, mock_usd):
    #     buy_coin_routine()

    @patch("investorbot.http.base.requests.get")
    def test_update_time_series_summaries_routine(self, mock_tickers):
        mock_tickers.return_value = Mock(ok=True)
        mock_tickers.return_value.json.side_effect = [
            get_mock_response("get-tickers-200.json"),
            get_mock_response("ts_data/ltc.json"),
            get_mock_response("ts_data/sol.json"),
            get_mock_response("ts_data/xrp.json"),
            get_mock_response("ts_data/beat.json"),
            get_mock_response("ts_data/doge.json"),
            get_mock_response("ts_data/avax.json"),
            get_mock_response("ts_data/shib.json"),
            get_mock_response("ts_data/ftm.json"),
        ]

        update_time_series_summaries_routine()

        market_analysis_items = self.mock_db_context_routines.get_market_analysis()

        self.assertEqual(
            len(market_analysis_items),
            1,
            "Expected one market analysis entry.",
        )

        ts_analysis = market_analysis_items[0]

        self.assertIsNotNone(ts_analysis)
        self.assertIsNotNone(ts_analysis.ts_data)

        self.assertEqual(len(ts_analysis.ts_data), 8)
        self.assertIsNotNone(ts_analysis.rating)
