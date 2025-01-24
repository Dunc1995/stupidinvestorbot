from investorbot.models import CoinProperties, CoinSelectionCriteria
from investorbot.integrations.cryptodotcom.structs import (
    InstrumentJson,
    OrderDetailJson,
    PositionBalanceJson,
)
from investorbot.structs.internal import OrderDetail, PositionBalance, RatingThreshold


def json_to_position_balance(balance: PositionBalanceJson) -> PositionBalance:
    return PositionBalance(
        coin_name=balance.instrument_name,
        market_value=float(balance.market_value),
        quantity=float(balance.quantity),
        reserved_quantity=float(balance.reserved_qty),
    )


def json_to_order_detail(json_data: OrderDetailJson) -> OrderDetail:
    return OrderDetail(
        status=json_data.status,
        order_id=json_data.client_oid,
        coin_name=json_data.instrument_name,
        order_value=float(json_data.order_value),
        quantity=float(json_data.quantity),
        cumulative_quantity=float(json_data.cumulative_quantity),
        cumulative_value=float(json_data.cumulative_value),
        cumulative_fee=float(json_data.cumulative_fee),
        fee_currency=json_data.fee_instrument_name,
        time_created_ms=int(json_data.create_time),
    )


def json_to_coin_properties(json_data: InstrumentJson) -> CoinProperties:
    return CoinProperties(
        json_data.symbol,
        float(json_data.qty_tick_size),
        int(json_data.quantity_decimals),
        float(json_data.price_tick_size),
        int(json_data.quote_decimals),
    )


def coin_selection_to_rating_threshold(
    options: CoinSelectionCriteria,
) -> RatingThreshold:
    return RatingThreshold(
        rating_id=options.rating_id,
        rating_upper_unbounded=options.rating_upper_unbounded,
        rating_upper_threshold=options.rating_upper_threshold,
        rating_lower_unbounded=options.rating_lower_unbounded,
        rating_lower_threshold=options.rating_lower_threshold,
    )
