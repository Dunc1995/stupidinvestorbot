import json
import logging
from requests.exceptions import HTTPError
from investorbot.constants import (
    INVESTMENT_INCREMENTS,
    DEFAULT_LOGS_NAME,
)
from investorbot import crypto_context, app_context
from investorbot.decorators import routine
from investorbot.validators import (
    LatestTradeValidator,
    LatestTradeValidatorOptions,
)
from investorbot.structs.internal import OrderStatuses
from investorbot.structs.egress import CoinPurchase
import investorbot.timeseries as timeseries
import investorbot.subroutines as subroutines

logger = logging.getLogger(DEFAULT_LOGS_NAME)
logging.basicConfig(level=logging.INFO)


@routine("Check Orders for Cancellation")
def cancel_orders_routine():
    no_deletions = True
    orders = app_context.get_all_buy_orders()

    for order in orders:
        order_detail = crypto_context.get_order_detail(order.buy_order_id)

        current_time = timeseries.time_now()
        age = timeseries.convert_ms_time_to_hours(
            current_time - order_detail.time_created_ms
        )

        if age > 0.15 and order_detail.status == OrderStatuses.ACTIVE.value:
            logger.info(f"Cancelling order {order.buy_order_id}")
            result = crypto_context.user.cancel_order(order.buy_order_id)
            app_context.delete_buy_order(order.buy_order_id)

            logger.info(str(result))
            no_deletions = False
        elif OrderStatuses.CANCELED.value == order_detail.status:
            logger.info(
                f"Removing order {order.buy_order_id} as it has been cancelled."
            )
            app_context.delete_buy_order(order.buy_order_id)

    if no_deletions:
        logger.info("No cancellable orders found.")


@routine("Time Series Update")
def update_time_series_summaries_routine():
    ts_summaries = []
    app_context.delete_existing_time_series()

    for latest_trade in crypto_context.get_latest_trades():
        logger.info(f"Fetching latest 24hr dataset for {latest_trade.coin_name}.")

        time_series_data = crypto_context.get_coin_time_series_data(
            latest_trade.coin_name
        )

        ts_summary = timeseries.get_coin_time_series_summary(
            latest_trade.coin_name, time_series_data
        )

        ts_summaries.append(ts_summary)

    app_context.add_items(ts_summaries)


@routine("Coin Purchase")
def buy_coin_routine():
    options = LatestTradeValidatorOptions(
        standard_deviation_threshold_should_exceed_threshold=True,
        standard_deviation_threshold=0.02,
        trend_line_percentage_threshold=0.01,
        trend_line_should_be_flat_or_rising=True,
        trade_needs_to_be_within_mean_and_lower_bound=True,
    )
    purchase_count = 0
    coin_count = crypto_context.get_investable_coin_count()

    logger.info(
        f"Searching for {coin_count} coins to invest in at ${INVESTMENT_INCREMENTS} each"
    )

    for latest_trade, ts_summary in subroutines.get_latest_trade_stats():
        if purchase_count == coin_count:
            logger.info("Maximum number of coin investments reached.")
            break

        validator = LatestTradeValidator(latest_trade, ts_summary, options)

        if not validator.is_valid_for_purchase():
            continue

        coin_name = latest_trade.coin_name

        logger.info(
            f"{coin_name} can be purchased based on current selection criteria."
        )

        coin_props = app_context.get_coin_properties(coin_name)

        spec = CoinPurchase(latest_trade.price, coin_props)

        buy_order = crypto_context.place_coin_buy_order(spec)
        app_context.add_item(buy_order)

        purchase_count += 1


@routine("Sell Coins")
def sell_coin_routine():
    buy_orders = app_context.get_all_buy_orders()

    for order in buy_orders:
        order_detail = crypto_context.get_order_detail(order.buy_order_id)

        coin_balance = crypto_context.get_coin_balance(order_detail.coin_name)

        print(json.dumps(order_detail.__dict__, indent=4))
        print(json.dumps(coin_balance.__dict__, indent=4))

        # logger.info(sell_order.__dict__)

        # if sell_order.value_ratio >= order_detail.minimum_acceptable_value_ratio:
        #     logger.info(f"Placing sell order for order {sell_order.buy_order_id}.")

        #     try:
        #         pass
        #         # crypto_context.place_coin_sell_order(sell_order)
        #     except HTTPError as error:
        #         logger.warn(
        #             "WARNING HTTP ERROR - continuing with script to ensure database consistency."
        #         )
        #         logger.warn(error.args[0])
