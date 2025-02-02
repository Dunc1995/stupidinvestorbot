from datetime import datetime, timedelta
import math
from investorbot.integrations.simulation.models import PositionBalanceSimulated
from investorbot.integrations.simulation.services import SimulatedCryptoService
from investorbot.routines import buy_coin_routine, refresh_market_analysis_routine


def test_market_analysis_can_be_executed_on_simulation(
    monkeypatch, mock_context_with_data
):
    """Simply running market analysis on simulated data."""
    crypto_service = mock_context_with_data.crypto_service

    if not isinstance(crypto_service, SimulatedCryptoService):
        raise TypeError("Crypto service needs to be simulated for this test.")

    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", quantity=100.0, reserved_quantity=0.0
    )

    crypto_service.simulation_db.add_wallet_entry(wallet_entry)

    # Patch routine services with in-memory variants.
    monkeypatch.setattr("investorbot.routines.bot_context", mock_context_with_data)

    # TODO add some assertions for what to expect after running this
    refresh_market_analysis_routine(hours=24)


def test_buy_order_routine_works_on_simulation(
    monkeypatch, mock_context, mock_static_time
):
    """Testing the simulation will track wallet balance correctly whilst placing
    buy orders."""

    # Need to override time implementation here to ensure there's sequential time order to this test
    monkeypatch.setattr(
        "investorbot.integrations.simulation.providers.env.time",
        mock_static_time,
    )

    monkeypatch.setattr(
        "investorbot.integrations.simulation.services.env.time",
        mock_static_time,
    )

    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", quantity=100.0, reserved_quantity=0.0
    )

    crypto_service = mock_context.crypto_service
    bot_db = mock_context.db_service

    if not isinstance(crypto_service, SimulatedCryptoService):
        raise TypeError("Crypto service should be simulated during simulation tests.")

    crypto_service.simulation_db.add_wallet_entry(wallet_entry)

    # Patch routine services with in-memory variants.
    monkeypatch.setattr("investorbot.routines.bot_context", mock_context)

    # TODO add some assertions for what to expect after running this
    buy_coin_routine()

    cash_balance = crypto_service.get_cash_balance()

    buy_order_count = len(bot_db.get_all_buy_orders())

    assert buy_order_count == 5, "Number of buy orders isn't correct."
    assert math.isclose(
        cash_balance.usd_balance, 50.0, abs_tol=1
    ), "Final wallet balance isn't correct."

    # Cash balance is expected to be a bit lower after fee deductions (0.5% fee)
    assert math.isclose(cash_balance.total_estimated_value_usd, 99.75, abs_tol=0.1)


# ! This test may be prone to failure if any lag is introduced
def test_time_remains_synchronized_whilst_running_buy_routine(
    monkeypatch, mock_context, mock_simulated_time
):
    """I am unsure how variable binding will behave with simulated time. This test ensures simulated
    time increments coincide with creation times in the bot's database."""

    monkeypatch.setattr(
        "investorbot.integrations.simulation.providers.env.time",
        mock_simulated_time,
    )

    monkeypatch.setattr(
        "investorbot.integrations.simulation.services.env.time",
        mock_simulated_time,
    )

    crypto_service = mock_context.crypto_service

    if not isinstance(crypto_service, SimulatedCryptoService):
        raise TypeError("Crypto service needs to be simulated for this test.")

    bot_db = mock_context.db_service

    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", quantity=100.0, reserved_quantity=0.0
    )

    crypto_service.simulation_db.add_wallet_entry(wallet_entry)

    monkeypatch.setattr("investorbot.routines.bot_context", mock_context)

    time_now = mock_simulated_time.now()
    time_now = time_now.replace(microsecond=0)

    current_time = datetime.now().replace(microsecond=0)

    assert time_now == current_time - timedelta(
        days=1
    ), "Initial time offset is not correct."

    mock_simulated_time.increment_time()  # adds 20 seconds.
    mock_simulated_time.increment_time()  # adds 20 seconds.
    mock_simulated_time.increment_time()  # adds 20 seconds.
    mock_simulated_time.increment_time()  # adds 20 seconds.
    mock_simulated_time.increment_time()  # adds 20 seconds.
    mock_simulated_time.increment_time()  # adds 20 seconds.

    new_time_now = mock_simulated_time.now()
    new_time_now = new_time_now.replace(microsecond=0)

    expected_time_now = (current_time - timedelta(days=1)) + timedelta(minutes=2)

    # Time should have passed by 2 minutes after the above increments.
    assert (
        new_time_now == expected_time_now
    ), "Time has not passed as expected whilst simulating time prior to running buy coin routine."

    buy_coin_routine()

    buy_orders = bot_db.get_all_buy_orders()

    buy_order = buy_orders[0]

    # ! Expecting creation time to equal time after the time increments above.
    assert (
        buy_order.creation_time.replace(microsecond=0) == expected_time_now
    ), "Buy order creation time was not correct."
