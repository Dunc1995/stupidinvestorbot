from datetime import datetime, timedelta
import math
import uuid
from investorbot.integrations.simulation.models import PositionBalanceSimulated
from investorbot.interfaces.services import ICryptoService
from investorbot.models import BuyOrder
from investorbot.structs.egress import CoinPurchase, CoinSale


def test_get_coin_balance_returns_latest_entry(
    mock_simulated_crypto_service, mock_static_time
):
    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", quantity=100.0, reserved_quantity=0.0
    )
    wallet_entry_two = PositionBalanceSimulated(
        coin_name="USD", quantity=110.0, reserved_quantity=0.0
    )
    wallet_entry_three = PositionBalanceSimulated(
        coin_name="USD", quantity=120.0, reserved_quantity=0.0
    )

    # time service automatically increments time for testing purposes.
    wallet_entry_two.creation_time = mock_static_time.now()
    wallet_entry_three.creation_time = mock_static_time.now()

    # Add three wallet entries with different creation times.
    mock_simulated_crypto_service.simulation_db.add_item(wallet_entry)
    mock_simulated_crypto_service.simulation_db.add_item(wallet_entry_two)
    mock_simulated_crypto_service.simulation_db.add_item(wallet_entry_three)

    # Use ICryptoService to avoid referencing simulation-specific functionality
    crypto_service: ICryptoService = mock_simulated_crypto_service

    balance = crypto_service.get_coin_balance("USD")

    assert balance.market_value == 120.0


def test_wallet_tracks_usd_balance_with_orders(
    mock_bot_db, mock_simulated_crypto_service
):
    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", quantity=100.0, reserved_quantity=0.0
    )

    mock_simulated_crypto_service.simulation_db.add_item(wallet_entry)

    # Use ICryptoService to avoid referencing simulation-specific functionality
    crypto_service: ICryptoService = mock_simulated_crypto_service

    usd_balance = crypto_service.get_usd_balance()

    assert usd_balance == 100.0, "Incorrect starting USD balance."

    coin_name = "ETH_USD"

    coin_props = mock_bot_db.get_coin_properties(coin_name)
    coin_buy_order = CoinPurchase(coin_props, 2000.0)

    buy_order = crypto_service.place_coin_buy_order(coin_buy_order)

    # Place buy order - this should detract from USD balance
    updated_usd_balance = crypto_service.get_usd_balance()

    updated_eth_balance = crypto_service.get_coin_balance("ETH")

    assert (
        updated_usd_balance == 90.0
    ), "Buy order has not been deducted from USD balance."

    buy_order_id = buy_order.buy_order_id
    mock_bot_db.add_item(buy_order)

    # Retrieving buy order from db just for completeness.
    order_detail = crypto_service.get_order_detail(buy_order_id)

    coin_sale = CoinSale(
        coin_props,
        2200.0,
        order_detail.quantity - order_detail.fee,
    )

    # Place sell order - this should add to USD balance
    crypto_service.place_coin_sell_order(buy_order_id, coin_sale)

    # Check money has been added back to USD balance
    final_usd_balance = crypto_service.get_usd_balance()

    # TODO implement better approach to market value
    final_eth_balance = crypto_service.get_coin_balance("ETH")

    assert math.isclose(
        final_usd_balance, 100.7261, abs_tol=1e-04
    ), "Final USD balance is not correct."


def test_cash_balance_is_correctly_calculated(
    mock_simulated_crypto_service, mock_static_time
):
    """Total cash balance should reflect the latest PositionBalance entries in the db. Here I'm
    expecting ONLY the modified balances to be summed.
    """
    modified_usd_balance = PositionBalanceSimulated(
        coin_name="USD",
        quantity=105.0,
        reserved_quantity=0.0,
    )

    # Time increments ensure the modified balances are the latest entries in the db.
    # Increment time
    modified_usd_balance.creation_time = mock_static_time.now()

    modified_eth_balance = PositionBalanceSimulated(
        coin_name="ETH",
        quantity=0.045,
        reserved_quantity=0.0,
    )

    # Forces market value to equal $20 for ETH (quantity * price_per_coin).
    mock_simulated_crypto_service.set_market_value_per_coin("ETH_USD", 444.444444)

    # Increment time
    modified_eth_balance.creation_time = mock_static_time.now()

    mock_simulated_crypto_service.simulation_db.add_items(
        [
            PositionBalanceSimulated(
                coin_name="USD",
                quantity=100.0,
                reserved_quantity=0.0,
            ),
            modified_usd_balance,
            PositionBalanceSimulated(
                coin_name="ETH",
                quantity=0.09,
                reserved_quantity=0.0,
            ),
            modified_eth_balance,
        ]
    )

    # Use ICryptoService to avoid referencing simulation-specific functionality
    crypto_service: ICryptoService = mock_simulated_crypto_service

    cash_balance = crypto_service.get_total_cash_balance()

    assert (
        cash_balance != 140.0
    ), "Cash balance needs to be calculated using latest entries - not all position balances."

    assert math.isclose(
        cash_balance, 125.0, abs_tol=1e-06
    ), "Calculated value is not correct."


def test_investable_coin_count_is_correct(mock_simulated_crypto_service):
    mock_simulated_crypto_service.simulation_db.add_items(
        [
            PositionBalanceSimulated(
                coin_name="USD",
                quantity=75.0,
                reserved_quantity=0.0,
            ),
            PositionBalanceSimulated(
                coin_name="ETH",
                quantity=0.07,
                reserved_quantity=0.0,
            ),
        ]
    )

    # Forces market value to equal $25 for ETH (quantity * price_per_coin).
    mock_simulated_crypto_service.set_market_value_per_coin("ETH_USD", 357.142857)

    crypto_service: ICryptoService = mock_simulated_crypto_service

    count = crypto_service.get_investable_coin_count()

    assert count == 2


def test_investable_coin_count_is_correct_two(mock_simulated_crypto_service):
    mock_simulated_crypto_service.simulation_db.add_items(
        [
            PositionBalanceSimulated(
                coin_name="USD",
                quantity=90.0,
                reserved_quantity=0.0,
            ),
            PositionBalanceSimulated(
                coin_name="ETH",
                quantity=0.07,
                reserved_quantity=0.0,
            ),
        ]
    )

    # Forces market value to equal $10 for ETH (quantity * price_per_coin).
    mock_simulated_crypto_service.set_market_value_per_coin("ETH_USD", 142.857142)

    crypto_service: ICryptoService = mock_simulated_crypto_service

    count = crypto_service.get_investable_coin_count()

    assert count == 4
