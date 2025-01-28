from datetime import datetime, timedelta
import math
import uuid
from investorbot.integrations.simulation.models import PositionBalanceSimulated
from investorbot.interfaces.services import ICryptoService
from investorbot.models import BuyOrder
from investorbot.structs.egress import CoinPurchase, CoinSale


def test_get_coin_balance_returns_latest_entry(mock_simulated_crypto_service):
    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", market_value=100.0, quantity=100.0, reserved_quantity=0.0
    )
    wallet_entry_two = PositionBalanceSimulated(
        coin_name="USD", market_value=110.0, quantity=110.0, reserved_quantity=0.0
    )
    wallet_entry_three = PositionBalanceSimulated(
        coin_name="USD", market_value=120.0, quantity=120.0, reserved_quantity=0.0
    )

    # time service automatically increments time for testing purposes.
    wallet_entry_two.time_creates_ms = mock_simulated_crypto_service.time_service.now()
    wallet_entry_three.time_creates_ms = (
        mock_simulated_crypto_service.time_service.now()
    )

    # Add three wallet entries with different creation times.
    mock_simulated_crypto_service.simulation_service.add_item(wallet_entry)
    mock_simulated_crypto_service.simulation_service.add_item(wallet_entry_two)
    mock_simulated_crypto_service.simulation_service.add_item(wallet_entry_three)

    # Use ICryptoService to avoid referencing simulation-specific functionality
    crypto_service: ICryptoService = mock_simulated_crypto_service

    balance = crypto_service.get_coin_balance("USD")

    assert balance.market_value == 120.0


def test_wallet_tracks_usd_balance_with_orders(
    mock_app_service, mock_simulated_crypto_service
):
    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", market_value=100.0, quantity=100.0, reserved_quantity=0.0
    )

    mock_simulated_crypto_service.simulation_service.add_item(wallet_entry)

    # Use ICryptoService to avoid referencing simulation-specific functionality
    crypto_service: ICryptoService = mock_simulated_crypto_service

    usd_balance = crypto_service.get_usd_balance()

    assert usd_balance == 100.0, "Incorrect starting USD balance."

    coin_name = "ETH_USD"

    coin_props = mock_app_service.get_coin_properties(coin_name)
    coin_buy_order = CoinPurchase(coin_props, 2000.0)

    buy_order = crypto_service.place_coin_buy_order(coin_buy_order)

    # Place buy order - this should detract from USD balance
    updated_usd_balance = crypto_service.get_usd_balance()

    updated_eth_balance = crypto_service.get_coin_balance("ETH")

    assert (
        updated_usd_balance == 90.0
    ), "Buy order has not been deducted from USD balance."

    buy_order_id = buy_order.buy_order_id
    mock_app_service.add_item(buy_order)

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
