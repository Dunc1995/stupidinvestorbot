import logging

from argh import arg
from investorbot.constants import (
    INVESTMENT_INCREMENTS,
    DEFAULT_LOGS_NAME,
)
from investorbot import crypto_service, app_service
from investorbot.decorators import routine
from investorbot.enums import OrderStatus
from investorbot.models import MarketAnalysis, TimeSeriesSummary
from investorbot.analysis import get_final_ranking
from investorbot.structs.egress import CoinPurchase, CoinSale
import investorbot.analysis as analysis

logger = logging.getLogger(DEFAULT_LOGS_NAME)
logging.basicConfig(level=logging.INFO)


@routine("Check Orders for Cancellation")
def cancel_orders_routine():
    """If any orders are taking too long to succeed, this routine will cancel the order and remove
    any reference to the unsuccessful order from the application database."""

    no_deletions = True
    orders = app_service.get_all_buy_orders()

    for order in orders:
        buy_order_id = order.buy_order_id
        order_detail = crypto_service.get_order_detail(buy_order_id)

        current_time = analysis.time_now()
        age = analysis.convert_ms_time_to_hours(
            current_time - order_detail.time_created_ms
        )

        if age > 0.15 and order_detail.status == OrderStatus.ACTIVE.value:
            logger.info(f"Cancelling order {buy_order_id}")
            result = crypto_service.user.cancel_order(buy_order_id)
            app_service.delete_buy_order(buy_order_id)

            logger.info(str(result))
            no_deletions = False
        elif OrderStatus.CANCELED.value == order_detail.status:
            logger.info(f"Removing order {buy_order_id} as it has been cancelled.")
            app_service.delete_buy_order(buy_order_id)

    if no_deletions:
        logger.info("No cancellable orders found.")


# TODO this method really needs refactoring.
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

    ts_summaries = []
    hours_int = int(hours)

    # Rating thresholds are basically a constant - they only exist in the database to the make the
    # app configurable.
    rating_thresholds = app_service.get_rating_thresholds()

    # Get latest trade prices for all instruments being sold at high trading volume and with USD.
    # TODO Parameterize trading currency rather than hardcoding USD. Also parameterize trading
    # volume threshold - this is being done implicitly at the moment.
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

    completed_ts_summaries = analysis.assign_outlier_properties(ts_summaries)

    confidence_rating = analysis.get_market_analysis_rating(
        completed_ts_summaries, rating_thresholds
    )

    market_analysis = MarketAnalysis(
        confidence_rating.value, analysis.time_now(), completed_ts_summaries
    )

    options = app_service.get_selection_criteria(confidence_rating.value)

    for ts_summary in market_analysis.ts_data:
        ts_summary.final_ranking = analysis.get_final_ranking(ts_summary, options)

    app_service.add_item(market_analysis)
    market_analysis, _ = app_service.get_market_analysis()

    return market_analysis


@routine("Coin Purchase")
def buy_coin_routine():
    """Fetches precalculated time series statistics for coins the application may decide to invest
    in. Buy orders will be placed for coins that meet the conditions set by a given ruleset.
    Rulesets are to be determined by the app's confidence in the market."""

    purchase_count = 0
    coin_count = crypto_service.get_investable_coin_count()

    logger.info(
        f"Searching for {coin_count} coins to invest in at ${INVESTMENT_INCREMENTS} each"
    )

    market_analysis, is_market_analysis_old = app_service.get_market_analysis()

    if is_market_analysis_old:
        market_analysis = refresh_market_analysis_routine()

    options = market_analysis.rating

    for ts_summary in market_analysis.ts_data:
        latest_trade = crypto_service.get_latest_trade(ts_summary.coin_name)

        if purchase_count == coin_count:
            logger.info("Maximum number of coin investments reached.")
            break

        if not get_final_ranking(ts_summary, options):
            logger.info(f"Rejected {ts_summary.coin_name}")
            continue

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
            continue

        # TODO potentially use websockets here to track the price.
        #
        # region Potential Web Socket Routine
        latest_trade = crypto_service.get_latest_trade(buy_order.coin_name)

        value_ratio = latest_trade.price / buy_order.price_per_coin

        if not analysis.is_value_ratio_sufficient(value_ratio, order_detail):
            continue

        coin_sale = CoinSale(
            buy_order.coin_properties,
            latest_trade.price,
            order_detail.order_quantity_minus_fee,
        )

        sell_order = crypto_service.place_coin_sell_order(
            buy_order.buy_order_id, coin_sale
        )
        app_service.add_item(sell_order)
        # endregion
