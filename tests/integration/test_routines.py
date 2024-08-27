import unittest
from unittest.mock import MagicMock, Mock, patch

from investorbot.contexts import AppContext, CryptoContext
from investorbot.db import init_db, app_context
from investorbot.enums import ConfidenceRating
from investorbot.models import BuyOrder
from investorbot.routines import (
    buy_coin_routine,
    sell_coin_routine,
    update_time_series_summaries_routine,
)
from tests.integration import get_mock_response


class TestRoutines(unittest.TestCase):

    @patch("investorbot.http.base.requests.get")
    def setUp(self, mock_instruments: MagicMock):
        mock_instruments.return_value = Mock(ok=True)
        mock_instruments.return_value.json.return_value = get_mock_response(
            "get-instruments"
        )

        app_context = AppContext("sqlite:///:memory:")
        crypto_context = CryptoContext()
        crypto_context.user.api_key = "Test984bvwhibwbiytesTy"
        crypto_context.user.api_secret_key = "Test_ounghTtgwth874hWWWTESTG"

        self.patcher_environment = patch(
            "investorbot.http.base.INVESTOR_APP_ENVIRONMENT", "Testing"
        )
        self.patcher_db_app_context = patch("investorbot.db.app_context", app_context)
        self.patcher_routine_app_context = patch(
            "investorbot.routines.app_context", app_context
        )
        self.patcher_routine_crypto_context = patch(
            "investorbot.routines.crypto_context", crypto_context
        )

        self.mock_environment = self.patcher_environment.start()
        self.mock_db_context_db = self.patcher_db_app_context.start()
        self.mock_db_context_routines = self.patcher_routine_app_context.start()
        self.mock_routine_crypto_context = self.patcher_routine_crypto_context.start()
        self.addCleanup(self.patcher_environment.stop)
        self.addCleanup(self.patcher_db_app_context.stop)
        self.addCleanup(self.patcher_routine_app_context.stop)
        self.addCleanup(self.patcher_routine_crypto_context.stop)

        init_db()

    @patch("investorbot.http.base.requests.get")
    def test_update_time_series_summaries_routine(self, mock_tickers):
        """The time series summary update routine iterates over time series data
        periodically and stores properties such as median, mean, trend line coefficient,
        etc. for each coin of interest. Market confidence can then be determined by
        collating all information for each coin and trying to spot an overall trend across
        the time series datasets. This test ensures market analysis results are correct
        after ingesting some example time series data.
        """
        mock_tickers.return_value = Mock(ok=True)
        mock_tickers.return_value.json.side_effect = [
            get_mock_response("get-tickers-200"),
            get_mock_response("ts_data/ltc"),
            get_mock_response("ts_data/sol"),
            get_mock_response("ts_data/xrp"),
            get_mock_response("ts_data/beat"),
            get_mock_response("ts_data/doge"),
            get_mock_response("ts_data/avax"),
            get_mock_response("ts_data/shib"),
            get_mock_response("ts_data/ftm"),
        ]

        update_time_series_summaries_routine()

        market_analysis = self.mock_db_context_routines.get_market_analysis()

        self.assertIsNotNone(market_analysis, "Market analysis was found to be None.")
        self.assertIsNotNone(
            market_analysis.ts_data, "Time series data was found to be None."
        )

        self.assertEqual(
            len(market_analysis.ts_data),
            8,
            "Incorrect number of time series data entries.",
        )
        self.assertIsNotNone(market_analysis.rating, "Rating was found to be None.")
        self.assertEqual(
            market_analysis.confidence_rating_id,
            ConfidenceRating.MODERATE_CONFIDENCE.value,
            "Confidence rating is not correct.",
        )

    # @patch("investorbot.crypto_context.get_usd_balance", return_value=27.65)
    # @patch("investorbot.crypto_context.get_investable_coin_count", return_value=5)
    # @patch("investorbot.http.base.requests.get")
    # def test(self, mock_tickers, mock_coin_count, mock_usd):
    #     self.test_update_time_series_summaries_routine()

    #     buy_coin_routine()

    # @patch("investorbot.crypto_context.get_usd_balance", return_value=27.65)
    # @patch("investorbot.crypto_context.get_investable_coin_count", return_value=5)
    @patch("investorbot.http.base.requests.post")
    def test_sell_coin_routine_stores_sell_order(self, mock_requests):
        """Testing the sell coin routine is able to distinguish between BuyOrders with
        an associated SellOrder and BuyOrders without. This behavior is necessary to
        prevent the application from repeatedly trying to make sell orders for the same
        BuyOrder.
        """
        mock_requests.return_value = Mock(ok=True)
        mock_requests.return_value.json.side_effect = [
            get_mock_response("doge-get-order-detail-200"),
            get_mock_response("user-balance-200"),
            get_mock_response("eth-get-order-detail-200"),
            get_mock_response("user-balance-200"),
            get_mock_response("create-order-200"),
        ]

        self.mock_db_context_routines.add_items(
            [
                BuyOrder("4310e324-8705-42d2-b15f-a5a62cb412d2", "DOGE_USD"),
                BuyOrder("a1d2bcb1-5991-41a1-833f-1db903258a1a", "ETH_USD"),
            ]
        )

        sell_coin_routine()

        doge_buy_order = self.mock_db_context_routines.get_buy_order(
            "4310e324-8705-42d2-b15f-a5a62cb412d2"
        )

        eth_buy_order = self.mock_db_context_routines.get_buy_order(
            "a1d2bcb1-5991-41a1-833f-1db903258a1a"
        )

        self.assertIsNone(
            doge_buy_order.sell_order,
            "DOGE sell order should be None as no order has been placed",
        )

        self.assertIsNotNone(eth_buy_order, "ETH buy order was found to be None")
        self.assertIsNotNone(
            eth_buy_order.sell_order,
            "ETH sell order is returning None when it should exist",
        )
