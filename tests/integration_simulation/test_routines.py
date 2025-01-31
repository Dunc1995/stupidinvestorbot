import math
from investorbot.context import BotContext
from investorbot.integrations.simulation.models import PositionBalanceSimulated
from investorbot.integrations.simulation.services import SimulatedCryptoService
from investorbot.routines import buy_coin_routine, refresh_market_analysis_routine


def test_market_analysis_can_be_executed_on_simulation(monkeypatch, mock_context):
    crypto_service = mock_context.crypto_service

    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", quantity=100.0, reserved_quantity=0.0
    )

    crypto_service.simulation_db.add_item(wallet_entry)

    # Patch routine services with in-memory variants.
    monkeypatch.setattr("investorbot.routines.bot_context", mock_context)

    # TODO add some assertions for what to expect after running this
    refresh_market_analysis_routine(hours=24)


def test_buy_order_routine_works_on_simulation(monkeypatch, mock_context):
    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", quantity=100.0, reserved_quantity=0.0
    )

    crypto_service = mock_context.crypto_service
    bot_db = mock_context.db_service

    if not isinstance(crypto_service, SimulatedCryptoService):
        raise TypeError("Crypto service should be simulated during simulation tests.")

    crypto_service.simulation_db.add_item(wallet_entry)

    # Patch routine services with in-memory variants.
    monkeypatch.setattr("investorbot.routines.bot_context", mock_context)

    # TODO add some assertions for what to expect after running this
    buy_coin_routine()

    final_usd_balance = crypto_service.get_usd_balance()
    cash_balance = crypto_service.get_total_cash_balance()

    buy_order_count = len(bot_db.get_all_buy_orders())

    assert buy_order_count == 5, "Number of buy orders isn't correct."
    assert math.isclose(
        final_usd_balance, 50.0, abs_tol=1
    ), "Final wallet balance isn't correct."

    # Cash balance is expected to be a bit lower after fee deductions (0.5% fee)
    assert math.isclose(cash_balance, 99.75, abs_tol=0.1)
