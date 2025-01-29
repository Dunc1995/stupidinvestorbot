from investorbot.integrations.simulation.models import PositionBalanceSimulated
from investorbot.routines import buy_coin_routine, refresh_market_analysis_routine


def test_market_analysis_can_be_executed_on_simulation(
    monkeypatch, mock_app_service, mock_simulated_crypto_service
):
    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", market_value=100.0, quantity=100.0, reserved_quantity=0.0
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
        coin_name="USD", market_value=100.0, quantity=100.0, reserved_quantity=0.0
    )

    mock_simulated_crypto_service.simulation_service.add_item(wallet_entry)

    # Patch routine services with in-memory variants.
    monkeypatch.setattr("investorbot.routines.app_service", mock_app_service)
    monkeypatch.setattr(
        "investorbot.routines.crypto_service", mock_simulated_crypto_service
    )

    # TODO add some assertions for what to expect after running this
    buy_coin_routine()
