import json
import math
import uuid
from investorbot import analysis
from investorbot.enums import OrderStatus
from investorbot.models import BuyOrder
from investorbot.structs.internal import OrderDetail, PositionBalance


def get_example_data(filename: str) -> dict:
    example_data = None

    with open(f"./tests/unit/fixtures/{filename}", "r") as f:
        example_data = json.loads(f.read())["result"]["data"]

    return example_data


# Values determined via Google Sheets
EXAMPLE_ONE_GRADIENT = -0.000197
EXAMPLE_ONE_GRADIENT_DECIMALS = 6
EXAMPLE_ONE_OFFSET = 4.53
EXAMPLE_ONE_OFFSET_DECIMALS = 2

EXAMPLE_TWO_GRADIENT = 0.0908
EXAMPLE_TWO_GRADIENT_DECIMALS = 4
EXAMPLE_TWO_OFFSET = 145
EXAMPLE_TWO_OFFSET_DECIMALS = 0


def __test_get_line_of_best_fit(
    filename: str,
    t_grad: float,
    t_grad_dec: int,
    t_offset: float,
    t_offset_dec: int,
):
    data = get_example_data(filename)

    stats, _ = analysis.get_time_series_data_frame(data)

    print(stats)

    a, b = analysis.get_line_of_best_fit(stats)

    gradient = round(float(a), t_grad_dec)
    offset = round(float(b), t_offset_dec)

    assert math.isclose(
        gradient, t_grad, abs_tol=float(f"1e-{t_grad_dec}")
    ), "Line of best fit gradient is incorrect"
    assert math.isclose(
        offset, t_offset, abs_tol=float(f"1e-{t_offset_dec}")
    ), "Line of best fit offset is incorrect"


def test_get_line_of_best_fit_one():
    """Testing I can replicate the trend line properties as calculated for the same dataset via
    Google Sheets."""
    __test_get_line_of_best_fit(
        "time-series-example-one.json",
        EXAMPLE_ONE_GRADIENT,
        EXAMPLE_ONE_GRADIENT_DECIMALS,
        EXAMPLE_ONE_OFFSET,
        EXAMPLE_ONE_OFFSET_DECIMALS,
    )


def test_get_line_of_best_fit_two():
    """Testing I can replicate the trend line properties as calculated for the same dataset via
    Google Sheets."""
    __test_get_line_of_best_fit(
        "time-series-example-two.json",
        EXAMPLE_TWO_GRADIENT,
        EXAMPLE_TWO_GRADIENT_DECIMALS,
        EXAMPLE_TWO_OFFSET,
        EXAMPLE_TWO_OFFSET_DECIMALS,
    )


def test_coin_sale_validator_is_ready_to_sell():
    """Covers basis for when all criteria has been met for the bot to sell a coin. It's now just
    a case of waiting for the coin value to reach an acceptable value."""
    buy_order = BuyOrder("123", "TON_USD", 6.6274)

    order_detail = OrderDetail(
        OrderStatus.COMPLETED.value,
        uuid.uuid4(),
        "TON_USD",
        4.970550,
        0.75,
        0.75,
        4.964925,
        0.00225,
        "TON",
        analysis.time_now() - 3_600_000,
    )
    position_balance = PositionBalance("TON", 4.88756072, 0.752975, 0.0)

    can_sell, _ = analysis.is_coin_sellable(buy_order, order_detail, position_balance)

    assert can_sell


def test_coin_sale_validator_will_not_sell_because_of_wallet_quantity():
    """A user may sell a coin manually, causing the original order quantity to be higher than
    what exists in the user's wallet. The bot needs to handle this gracefully."""
    buy_order = BuyOrder("123", "TON_USD", 6.6274)

    order_detail = OrderDetail(
        OrderStatus.COMPLETED.value,
        uuid.uuid4(),
        "TON_USD",
        4.970550,
        0.75,
        0.75,
        4.964925,
        0.00225,
        "TON",
        analysis.time_now() - 3_600_000,
    )
    position_balance = PositionBalance("TON", 0.056123, 0.01, 0.0)

    can_sell, validator = analysis.is_coin_sellable(
        buy_order, order_detail, position_balance
    )

    assert not validator.order_has_not_been_filled
    assert validator.wallet_balance_is_not_sufficient
    assert not can_sell


def test_coin_sale_validator_will_not_break_on_small_coin_balance():
    """A user may have a small amount of coin available whilst they have a pending buy order.
    This needs to be handled gracefully by the validator."""
    buy_order = BuyOrder("123", "TON_USD", 6.6274)

    order_detail = OrderDetail(
        OrderStatus.OTHER.value,
        uuid.uuid4(),
        "TON_USD",
        4.970550,
        0.75,
        0.00,
        0.00,
        0.00,
        "TON",
        analysis.time_now() - 3_600_000,
    )
    position_balance = PositionBalance("TON", 0.056123, 0.01, 0.0)

    can_sell, validator = analysis.is_coin_sellable(
        buy_order, order_detail, position_balance
    )

    assert validator.order_has_not_been_filled
    assert not validator.wallet_balance_is_not_sufficient
    assert not can_sell


def test_coin_sale_validator_will_not_break_on_normal_coin_balance():
    """A user may have an amount of coin available whilst they have a pending buy order. This
    needs to be handled gracefully by the validator."""
    buy_order = BuyOrder("123", "TON_USD", 6.6274)

    order_detail = OrderDetail(
        OrderStatus.OTHER.value,
        uuid.uuid4(),
        "TON_USD",
        4.970550,
        0.75,
        0.00,
        0.00,
        0.00,
        "TON",
        analysis.time_now() - 3_600_000,
    )
    position_balance = PositionBalance("TON", 5.3, 0.8, 0.0)

    can_sell, validator = analysis.is_coin_sellable(
        buy_order, order_detail, position_balance
    )

    assert validator.order_has_not_been_filled
    assert not validator.wallet_balance_is_not_sufficient
    assert not validator.no_coin_balance
    assert not validator.order_has_been_cancelled
    assert not validator.order_balance_has_already_been_sold
    assert not can_sell
