import logging
from investorbot.constants import (
    INVESTMENT_INCREMENTS,
    DEFAULT_LOGS_NAME,
)
from investorbot import crypto_service, app_service
from investorbot.decorators import routine
from investorbot.enums import OrderStatus
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


@routine("Time Series Update")
def update_time_series_summaries_routine():
    """Fetches time series data from the Crypto API and calculates various parameters according to
    each dataset - e.g. median, mean, modes, line-of-best-fit, etc. - these values are then stored
    in the application database via the TimeSeriesSummary models."""

    ts_summaries = []
    app_service.delete_existing_time_series()

    for latest_trade in crypto_service.get_latest_trades():
        logger.info(f"Fetching latest 24hr dataset for {latest_trade.coin_name}.")

        time_series_data = crypto_service.get_coin_time_series_data(
            latest_trade.coin_name
        )

        ts_summary = timeseries.get_coin_time_series_summary(
            latest_trade.coin_name, time_series_data
        )

        ts_summaries.append(ts_summary)

    rating_thresholds = app_service.get_rating_thresholds()

    confidence_rating = timeseries.get_market_analysis_rating(
        ts_summaries, rating_thresholds
    )

    market_analysis = MarketAnalysis(
        confidence_rating.value, timeseries.time_now(), ts_summaries
    )

    app_service.add_item(market_analysis)


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

    market_analysis = app_service.get_market_analysis(
        update_time_series_summaries_routine
    )
    options = market_analysis.rating

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
