import logging
from typing import Tuple
from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.enums import OrderStatus
from investorbot.structs.internal import (
    OrderDetail,
    PositionBalance,
    SaleValidationResult,
)
from investorbot.models import BuyOrder, CoinSelectionCriteria, TimeSeriesSummary
from investorbot.timeseries import time_now

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def is_coin_purchaseable(
    summary: TimeSeriesSummary, options: CoinSelectionCriteria
) -> bool:
    criteria = []

    if options.trend_line_should_be_falling:
        criteria.append(summary.is_trend_falling)

    if options.trend_line_should_be_flat:
        criteria.append(summary.is_trend_flat)

    if options.trend_line_should_be_rising:
        criteria.append(summary.is_trend_rising)

    if options.trend_line_should_be_flat_or_rising:
        criteria.append(summary.is_trend_flat or summary.is_trend_rising)

    return all(i for i in criteria)


def is_coin_sellable(
    buy_order: BuyOrder, order_detail: OrderDetail, coin_balance: PositionBalance | None
) -> Tuple[bool, SaleValidationResult]:
    no_coin_balance = coin_balance is None
    order_balance_has_already_been_sold = buy_order.sell_order is not None
    order_has_been_cancelled = order_detail.status == OrderStatus.CANCELED.value
    order_has_not_been_filled = order_detail.status != OrderStatus.FILLED.value
    wallet_balance_is_not_sufficient = (
        coin_balance.sellable_quantity < order_detail.order_quantity_minus_fee
        if coin_balance is not None
        else True
    )

    return not any(
        [
            no_coin_balance,
            order_balance_has_already_been_sold,
            order_has_been_cancelled,
            order_has_not_been_filled,
            wallet_balance_is_not_sufficient,
        ]
    ), SaleValidationResult(
        no_coin_balance,
        order_balance_has_already_been_sold,
        order_has_been_cancelled,
        order_has_not_been_filled,
        wallet_balance_is_not_sufficient,
    )


def __hours_since_order(order: OrderDetail) -> float:
    t_now = time_now()

    time_of_order = order.time_created_ms
    milliseconds_since_order = t_now - time_of_order
    return milliseconds_since_order / (1000 * 60 * 60)


def __get_minimum_acceptable_value_ratio(order: OrderDetail) -> float:
    # TODO make this configurable as DecayEquationParameters or similar. High confidence in the
    # market should result in slower decay rate.
    return 0.98 + 0.03 ** ((0.01 * __hours_since_order(order)) + 1.0)


def is_value_ratio_sufficient(value_ratio: float, order: OrderDetail) -> bool:
    return value_ratio >= __get_minimum_acceptable_value_ratio(order)
