import logging
from investorbot.constants import (
    INVESTMENT_INCREMENTS,
    DEFAULT_LOGS_NAME,
)
from investorbot import crypto_service, app_service
from investorbot.decorators import routine
from investorbot.enums import ConfidenceRating, OrderStatus
from investorbot.models import MarketAnalysis
from investorbot.validation import LatestTradeValidator
from investorbot.structs.egress import CoinPurchase, CoinSale
import investorbot.timeseries as timeseries
import investorbot.validation as validation

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

        current_time = timeseries.time_now()
        age = timeseries.convert_ms_time_to_hours(
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


@routine("Market Analysis")
def refresh_market_analysis_routine() -> MarketAnalysis:
    """Fetches time series data from the Crypto API and calculates various parameters according to
    each dataset - e.g. median, mean, modes, line-of-best-fit, etc. - these values are then stored
    in the application database via the TimeSeriesSummary models."""

    ts_summaries = []

    for latest_trade in crypto_service.get_latest_trades():
        logger.info(f"Fetching latest 24hr dataset for {latest_trade.coin_name}.")

        time_series_data = crypto_service.get_coin_time_series_data(
            latest_trade.coin_name
        )

        ts_summary = timeseries.get_coin_time_series_summary(
            latest_trade.coin_name, time_series_data
        )

        ts_summaries.append(ts_summary)

    # TODO find a way to pass property names using the TimeSeriesSummary class rather than
    # hardcoding strings.
    ts_summaries_first_iter = timeseries.get_outliers_in_time_series_data(
        ts_summaries,
        "normalized_line_of_best_fit_coefficient",
        "is_outlier_in_gradient",
    )

    ts_summaries_second_iter = timeseries.get_outliers_in_time_series_data(
        ts_summaries_first_iter,
        "normalized_value_24_hours_ago",
        "is_outlier_in_offset",
    )

    gradient_outliers = [
        ts_summary
        for ts_summary in ts_summaries_second_iter
        if ts_summary.is_outlier_in_gradient
    ]
    deviation_candidates = [
        ts_summary
        for ts_summary in ts_summaries_second_iter
        if not ts_summary.is_outlier_in_gradient
    ]

    deviation_subset = timeseries.get_outliers_in_time_series_data(
        deviation_candidates,
        "normalized_std",
        "is_outlier_in_deviation",
    )

    final_ts_summaries = gradient_outliers + deviation_subset

    rating_thresholds = app_service.get_rating_thresholds()

    confidence_rating = timeseries.get_market_analysis_rating(
        final_ts_summaries, rating_thresholds
    )

    market_analysis = MarketAnalysis(
        confidence_rating.value, timeseries.time_now(), final_ts_summaries
    )

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

    if market_analysis.rating.rating_id == ConfidenceRating.NO_CONFIDENCE.value:
        logger.warn(
            "No confidence in the current market. Not investing at this point in time."
        )
        return

    for ts_summary in market_analysis.ts_data:
        latest_trade = crypto_service.get_latest_trade(ts_summary.coin_name)

        if purchase_count == coin_count:
            logger.info("Maximum number of coin investments reached.")
            break

        validator = LatestTradeValidator(latest_trade, ts_summary, options)

        if not validator.is_valid_for_purchase():
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

    buy_orders = app_service.get_all_buy_orders()

    for buy_order in buy_orders:
        order_detail = crypto_service.get_order_detail(buy_order.buy_order_id)
        coin_balance = crypto_service.get_coin_balance(order_detail.coin_name)

        coin_is_sellable, validation_result = validation.is_coin_sellable(
            buy_order, order_detail, coin_balance
        )

        if validation_result.order_has_been_cancelled:
            app_service.delete_buy_order(buy_order.buy_order_id)

        if not coin_is_sellable:
            continue

        latest_trade = crypto_service.get_latest_trade(buy_order.coin_name)

        value_ratio = latest_trade.price / buy_order.price_per_coin

        if not validation.is_value_ratio_sufficient(value_ratio, order_detail):
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
