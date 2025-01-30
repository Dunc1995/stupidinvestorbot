import math
from investorbot.integrations.simulation.models import PositionBalanceSimulated
from investorbot.routines import buy_coin_routine, refresh_market_analysis_routine


def test_market_analysis_can_be_executed_on_simulation(
    monkeypatch, mock_app_service, mock_simulated_crypto_service
):
    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", quantity=100.0, reserved_quantity=0.0
    )

    mock_simulated_crypto_service.simulation_service.add_item(wallet_entry)

    # Patch routine services with in-memory variants.
    monkeypatch.setattr("investorbot.routines.app_service", mock_app_service)
    monkeypatch.setattr(
        "investorbot.routines.crypto_service", mock_simulated_crypto_service
    )

    # TODO add some assertions for what to expect after running this
    refresh_market_analysis_routine(hours=24)


def test_buy_order_routine_works_on_simulation(
    monkeypatch, mock_app_service, mock_simulated_crypto_service
):
    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", quantity=100.0, reserved_quantity=0.0
    )

    mock_simulated_crypto_service.simulation_service.add_item(wallet_entry)

    # Patch routine services with in-memory variants.
    monkeypatch.setattr("investorbot.routines.app_service", mock_app_service)
    monkeypatch.setattr(
        "investorbot.routines.crypto_service", mock_simulated_crypto_service
    )

    # TODO add some assertions for what to expect after running this
    buy_coin_routine()

    final_usd_balance = mock_simulated_crypto_service.get_usd_balance()
    cash_balance = mock_simulated_crypto_service.get_total_cash_balance()

    buy_order_count = len(mock_app_service.get_all_buy_orders())

    assert buy_order_count == 5, "Number of buy orders isn't correct."
    assert math.isclose(
        final_usd_balance, 50.0, abs_tol=1
    ), "Final wallet balance isn't correct."

    # Cash balance is expected to be a bit lower after fee deductions (0.5% fee)
    assert math.isclose(cash_balance, 99.75, abs_tol=0.1)
