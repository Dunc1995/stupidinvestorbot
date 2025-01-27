from datetime import datetime, timedelta
from typing import Tuple
import pytest

from investorbot.enums import AppIntegration
from investorbot.integrations.simulation.models import PositionBalanceSimulated
from investorbot.integrations.simulation.services import (
    SimulatedCryptoService,
    SimulationService,
)
from investorbot.interfaces.services import ICryptoService


@pytest.fixture(autouse=True)
def set_environment(monkeypatch):
    monkeypatch.setattr(
        "investorbot.INVESTOR_APP_INTEGRATION",
        str(AppIntegration.SIMULATED),
    )


@pytest.fixture
def mock_simulated_crypto_service() -> ICryptoService:
    simulation_service = SimulationService("sqlite:///:memory:")

    simulation_service.run_migration()

    wallet_entry = PositionBalanceSimulated(
        coin_name="USD", market_value=100.0, quantity=100.0, reserved_quantity=0.0
    )
    wallet_entry_two = PositionBalanceSimulated(
        coin_name="USD", market_value=110.0, quantity=110.0, reserved_quantity=0.0
    )
    wallet_entry_three = PositionBalanceSimulated(
        coin_name="USD", market_value=120.0, quantity=120.0, reserved_quantity=0.0
    )

    wallet_entry_two.time_creates_ms = datetime.now() + timedelta(days=1)
    wallet_entry_three.time_creates_ms = datetime.now() + timedelta(days=2)

    simulation_service.add_item(wallet_entry)
    simulation_service.add_item(wallet_entry_two)
    simulation_service.add_item(wallet_entry_three)

    crypto_service = SimulatedCryptoService(simulation_service)

    return crypto_service

    # result = crypto_service.get_coin_balance("USD")
    # print(result)
