from requests import Response

from investorbot.enums import MarketCharacterization
from investorbot.models import BuyOrder
from investorbot.routines import (
    sell_coin_routine,
    refresh_market_analysis_routine,
)
from investorbot.structs.internal import LatestTrade


def test_update_time_series_summaries_routine(
    monkeypatch, get_file_data, mock_app_service, mock_crypto_service
):
    """The time series summary update routine iterates over time series data periodically and
    stores properties such as median, mean, trend line coefficient, etc. for each coin of
    interest. Market confidence can then be determined by collating all information for each
    coin and trying to spot an overall trend across the time series datasets. This test ensures
    market analysis results are correct after ingesting some example time series data.
    """

    LATEST_TRADES = [
        LatestTrade("FTM_USD", 0.000013422),
        LatestTrade("SHIB_USD", 0.000013422),
        LatestTrade("AVAX_USD", 20.448),
        LatestTrade("SOL_USD", 143.99),
        LatestTrade("XRP_USD", 0.56686),
        LatestTrade("LTC_USD", 66.547),
        LatestTrade("BEAT_USD", 0.002535),
        LatestTrade("DOGE_USD", 0.101400),
    ]

    # Patch routine services with in-memory variants.
    monkeypatch.setattr("investorbot.routines.app_service", mock_app_service)
    monkeypatch.setattr("investorbot.routines.crypto_service", mock_crypto_service)

    # Allows the routine to iterate through latest trades and query their corresponding timeseries
    # data.
    monkeypatch.setattr(
        "investorbot.routines.crypto_service.get_latest_trades", lambda: LATEST_TRADES
    )

    def mock_get_request(query_string: str) -> dict:
        """A list of eight 'LatestTrade' instances means this method will be called eight times.
        Each time it is grabbing the coin name to point to its corresponding dummy data file.
        """

        # query_string is of the format "get-valuation?instrument_name={filename}_USD&..."
        filename = query_string.lower().split("=")[1].split("&")[0].split("_")[0]

        response = Response()
        response.status_code = 200
        response.json = lambda: get_file_data(f"ts_data/{filename}")

        return response

    # Ensure network calls are patched.
    monkeypatch.setattr("requests.get", mock_get_request)

    #! Run the routine
    refresh_market_analysis_routine(hours=24)

    # Grab the market_analysis object as generated by the refresh_market_analysis_routine.
    market_analysis, _ = mock_app_service.get_market_analysis()

    assert market_analysis is not None, "Market analysis was found to be None."
    assert market_analysis.ts_data is not None, "Time series data was found to be None."

    assert (
        len(market_analysis.ts_data) == 8
    ), "Incorrect number of time series data entries."
    assert market_analysis.rating is not None, "Rating was found to be None."
    assert (
        market_analysis.confidence_rating_id == MarketCharacterization.RISING.value
    ), "Confidence rating is not correct."


def test_sell_coin_routine_stores_sell_order(
    monkeypatch, get_file_data, mock_app_service, mock_crypto_service
):
    """Testing the sell coin routine is able to distinguish between BuyOrders with an associated
    SellOrder and BuyOrders without. This behavior is necessary to prevent the application from
    repeatedly trying to make sell orders for the same BuyOrder."""

    DOGE_GUID = "4310e324-8705-42d2-b15f-a5a62cb412d2"
    ETH_GUID = "a1d2bcb1-5991-41a1-833f-1db903258a1a"

    monkeypatch.setattr("investorbot.routines.app_service", mock_app_service)
    monkeypatch.setattr("investorbot.routines.crypto_service", mock_crypto_service)

    # Post requests replicate all calls made as the sell routine iterates through BuyOrders added
    # to the mock_app_service db.
    def mock_post_request(method, **kwargs) -> dict:
        filename = None
        response = Response()
        response.status_code = 200

        if "user-balance" in method:
            filename = "user-balance-200"
        elif "create-order" in method:
            filename = "create-order-200"
        else:
            # ! This is prone to breaking
            guid = kwargs["json"]["params"]["client_oid"]

            if guid == DOGE_GUID:
                filename = "doge-get-order-detail-200"
            elif guid == ETH_GUID:
                filename = "eth-get-order-detail-200"

        response.json = lambda: get_file_data(filename)

        return response

    # Replicates the get request made on get_latest_trade
    def mock_get_request(*args) -> dict:
        """Only one get request is made here."""
        response = Response()
        response.status_code = 200
        response.json = lambda: get_file_data("get-tickers-eth-200")

        return response

    mock_app_service.add_items(
        [
            BuyOrder(DOGE_GUID, "DOGE_USD", 3.0),
            BuyOrder(ETH_GUID, "ETH_USD", 3.0),
        ]
    )

    # Ensure network calls are patched
    monkeypatch.setattr("requests.get", mock_get_request)
    monkeypatch.setattr("requests.post", mock_post_request)

    #! Run the routine
    sell_coin_routine()

    doge_buy_order = mock_app_service.get_buy_order(DOGE_GUID)
    eth_buy_order = mock_app_service.get_buy_order(ETH_GUID)

    # Ensures no order has been placed for DOGE coin.
    assert (
        doge_buy_order.sell_order is None
    ), "DOGE sell order should be None as no order has been placed"

    assert eth_buy_order is not None, "ETH buy order was found to be None"

    # Ensures a sell order has been placed by the sell_coin_routine() call.
    assert (
        eth_buy_order.sell_order is not None
    ), "ETH sell order is returning None when it should exist"
