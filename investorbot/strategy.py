"""Trading strategy and decision logic.

This module contains business logic for buy/sell decisions. Statistical computation lives in
investorbot.analysis — this module consumes analysis results to make trading decisions.
"""

import logging
from typing import List, Tuple

from investorbot.constants import DEFAULT_LOGS_NAME
from investorbot.enums import OrderStatus, TrendLineState
from investorbot.interfaces.providers import ITimeProvider
from investorbot.models import (
    BuyOrder,
    CoinSelectionCriteria,
    TimeSeriesSummary,
)
from investorbot.structs.internal import (
    OrderDetail,
    PositionBalance,
    SaleValidationResult,
)

logger = logging.getLogger(DEFAULT_LOGS_NAME)


def _hours_since_order(order: OrderDetail, time_provider: ITimeProvider) -> float:
    t_now = time_provider.now_in_ms()
    time_of_order = order.time_created_ms
    milliseconds_since_order = t_now - time_of_order
    return milliseconds_since_order / (1000 * 60 * 60)


def _get_minimum_acceptable_value_ratio(
    order: OrderDetail, time_provider: ITimeProvider
) -> float:
    # TODO make this configurable as DecayEquationParameters or similar. High confidence in the
    # market should result in slower decay rate.
    return 0.99 + 0.03 ** ((0.01 * _hours_since_order(order, time_provider)) + 1.0)


def is_value_ratio_sufficient(
    value_ratio: float, order: OrderDetail, time_provider: ITimeProvider
) -> bool:
    """Check whether the current value ratio meets the minimum acceptable threshold.

    The threshold decays over time — the longer a position is held, the lower the required
    return before selling. This encourages the bot to cut losses on stale positions.
    """
    return value_ratio >= _get_minimum_acceptable_value_ratio(order, time_provider)


def assign_weighted_rankings(
    summaries: List[TimeSeriesSummary], options: CoinSelectionCriteria
) -> List[TimeSeriesSummary]:
    """Apply selection criteria weights to each coin's ranking."""
    for summary in summaries:
        ranking = summary.initial_ranking

        params = [
            options.coin_should_be_volatile and summary.is_volatile,
            options.coin_should_be_nominal and not summary.is_outlier_in_gradient,
            options.coin_should_be_an_outlier and summary.is_outlier_in_gradient,
            options.trend_line_should_be_falling
            and summary.trend_state == TrendLineState.FALLING,
            options.trend_line_should_be_flat
            and summary.trend_state == TrendLineState.FLAT,
            options.trend_line_should_be_rising
            and summary.trend_state == TrendLineState.RISING,
        ]

        for param in params:
            if param:
                ranking += 100

        summary.final_ranking = ranking

    return summaries


def is_coin_sellable(
    buy_order: BuyOrder,
    order_detail: OrderDetail,
    coin_balance: PositionBalance | None,
) -> Tuple[bool, SaleValidationResult]:
    """Determine whether a buy order can be sold based on order status and wallet balance."""
    no_coin_balance = coin_balance is None or coin_balance.quantity == 0.0
    order_balance_has_already_been_sold = buy_order.sell_order is not None
    order_has_been_cancelled = order_detail.status == OrderStatus.CANCELED
    order_has_not_been_filled = order_detail.status != OrderStatus.COMPLETED
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
