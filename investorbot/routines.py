import logging

from argh import arg
from requests import HTTPError
from investorbot.constants import (
    INVESTMENT_INCREMENTS,
    DEFAULT_LOGS_NAME,
)
from investorbot import crypto_service, app_service
from investorbot.decorators import routine
from investorbot.models import CashBalance, MarketAnalysis
from investorbot.structs.egress import CoinPurchase, CoinSale
import investorbot.analysis as analysis

logger = logging.getLogger(DEFAULT_LOGS_NAME)
logging.basicConfig(level=logging.INFO)


def get_initial_ts_summaries(hours_int):
    ts_summaries = []

    # Get latest trade prices for all instruments being sold at high trading volume and with USD.
    # TODO Parameterize trading currency rather than hardcoding USD. Also parameterize trading
    # volume threshold - this is being done implicitly in get_latest_trades currently.
    for latest_trade in crypto_service.get_latest_trades():
        logger.info(
            f"Fetching latest {hours_int} hour's worth of data for {latest_trade.coin_name}."
        )

        # Time series data refers to x number of hours' worth of data for a particular instrument or
        # 'coin'.
        time_series_data = crypto_service.get_coin_time_series_data(
            latest_trade.coin_name, hours_int
        )

        # Convert timeseries data into summary object.
        ts_summary = analysis.get_coin_time_series_summary(
            latest_trade.coin_name, time_series_data
        )

        # Add to the list of summary objects.
        ts_summaries.append(ts_summary)

    return ts_summaries


def get_coins_to_purchase():
    coin_count = crypto_service.get_investable_coin_count()

    log_message = (
        f"Searching for {coin_count} coins to invest in at ${INVESTMENT_INCREMENTS} each"
        if coin_count > 0
        else "Coin investments at capacity."
    )

    logger.info(log_message)

    return (
        [latest_trade.coin_name for latest_trade in crypto_service.get_latest_trades()][
            -coin_count:
        ]
        if coin_count > 0
        else []
    )


@arg(
    "hours",
    default=24,
    help="The number of hour's worth of data required for the market analysis.",
)
@routine("Market Analysis")
def refresh_market_analysis_routine(hours: int) -> MarketAnalysis:
    """Fetches time series data from the Crypto API and calculates various parameters according to
    each dataset - e.g. median, mean, modes, line-of-best-fit, etc. - these values are then stored
    in the application database via the TimeSeriesSummary models."""

    hours_int = int(hours)
    initial_ts_summaries = get_initial_ts_summaries(hours_int)

    # Rating thresholds are basically a constant - they only exist in the database to the make the
    # app configurable. FIXME - Rating thresholds are a subset of coin_selection_criteria -
    # unnecessarily complicated.
    rating_thresholds = app_service.get_rating_thresholds()

    # Compare coins and attribute outlier properties to coins with any kind of weird property.
    partially_complete_ts_summaries = analysis.assign_outlier_properties(
        initial_ts_summaries
    )

    # Assign the market analysis with a confidence rating to quantify how well the market is doing.
    confidence_rating = analysis.get_market_analysis_rating(
        partially_complete_ts_summaries, rating_thresholds
    )

    # Fetch the selection criteria based on current market confidence.
    options = app_service.get_selection_criteria(confidence_rating.value)

    # Use selection criteria to apply weightings to each coin's rank.
    complete_ts_summaries = analysis.assign_weighted_rankings(
        partially_complete_ts_summaries, options
    )

    # Create the final market analysis object to add to the db.
    market_analysis = MarketAnalysis(
        confidence_rating.value, analysis.time_now(), complete_ts_summaries
    )

    app_service.add_item(market_analysis)

    # Refetch the market analysis here to ensure ORM model is in sync with database.
    market_analysis, _ = app_service.get_market_analysis()

    return market_analysis


@routine("Coin Purchase")
def buy_coin_routine():
    """Fetches precalculated time series statistics for coins the application may decide to invest
    in. Buy orders will be placed for coins that meet the conditions set by a given ruleset.
    Rulesets are to be determined by the app's confidence in the market."""

    purchase_count = 0
    coin_names = get_coins_to_purchase()
    coin_count = len(coin_names)

    for coin_name in coin_names:
        latest_trade = crypto_service.get_latest_trade(coin_name)

        if purchase_count == coin_count:
            logger.info("Maximum number of coin investments reached.")
            break

        coin_name = latest_trade.coin_name

        logger.info(
            f"{coin_name} can be purchased based on current selection criteria."
        )

        coin_props = app_service.get_coin_properties(coin_name)

        spec = CoinPurchase(coin_props, latest_trade.price)

        buy_order = crypto_service.place_coin_buy_order(spec)
        app_service.add_item(buy_order)

        purchase_count += 1


@routine("Sell Coins")
def sell_coin_routine():
    """Pulls all BuyOrders from the application database, fetches corresponding data via the Crypto
    API and cross-references this with the user's wallet to verify that a SELL trade can be placed.
    SELL orders will then be placed for coin balances that have met the minimum return threshold -
    e.g. 101 percent of the original BuyOrder value."""

    # Get all buy orders that have been placed by the app.
    buy_orders = app_service.get_all_buy_orders()

    for buy_order in buy_orders:
        # Get order details from Crypto.com - at this the point the order could be in various states
        # such as: 'EXPIRED', 'CANCELED', 'FILLED', etc. - in other words the order may not yet be
        # in a state to sell.
        order_detail = crypto_service.get_order_detail(buy_order.buy_order_id)

        # Attempt to fetch the user's current balance for a particular coin. coin_balance will be
        # None here if the order has not yet been filled and the user has none of the currency in
        # question.
        coin_balance = crypto_service.get_coin_balance(order_detail.coin_name)

        # coin_is_sellable is a binary 'True' if the buy order is sellable, 'False' if not.
        # validation_result is used to access reasons as to why the buy order is currently not
        # sellable.
        coin_is_sellable, validation_result = analysis.is_coin_sellable(
            buy_order, order_detail, coin_balance
        )

        # If the buy order has been cancelled, there's no reason to store the order id in the
        # database, hence delete any reference to the order.
        if validation_result.order_has_been_cancelled:
            app_service.delete_buy_order(buy_order.buy_order_id)

        # No further action required if the buy order cannot be sold at this time.
        if not coin_is_sellable:
            logger.info(validation_result.reasoning(buy_order.coin_name))
            continue

        # TODO potentially use websockets here to track the price.
        #
        # region Potential Web Socket Routine
        latest_trade = crypto_service.get_latest_trade(buy_order.coin_name)

        value_ratio = latest_trade.price / buy_order.price_per_coin

        if not analysis.is_value_ratio_sufficient(value_ratio, order_detail):
            logger.info(f"Value ratio {value_ratio} not sufficient.")
            continue

        coin_sale = CoinSale(
            buy_order.coin_properties,
            latest_trade.price,
            order_detail.order_quantity_minus_fee,
        )

        logger.info(
            f"Selling {coin_sale.coin_properties.coin_name} at value ratio {value_ratio}"
        )

        try:
            sell_order = crypto_service.place_coin_sell_order(
                buy_order.buy_order_id, coin_sale
            )
            app_service.add_item(sell_order)
        except HTTPError as http_error:
            # ! FIXME need to find the specific error here rather than hiding 500 errors.
            if http_error.response.status_code != 500:
                raise http_error
            else:
                logger.warning(http_error)
                logger.info("Continuing with routine...")
        # endregion

    cash_balance = crypto_service.get_total_cash_balance()
    app_service.add_item(CashBalance(cash_balance))
