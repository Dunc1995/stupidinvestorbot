import pytest

from investorbot.enums import AppIntegration
from investorbot.integrations.simulation.services import (
    SimulatedCryptoService,
    SimulationService,
    TestingTime,
)


@pytest.fixture(autouse=True)
def set_environment(monkeypatch):
    monkeypatch.setattr(
        "investorbot.INVESTOR_APP_INTEGRATION",
        str(AppIntegration.SIMULATED),
    )


@pytest.fixture
def mock_simulated_crypto_service() -> SimulatedCryptoService:
    simulation_service = SimulationService("sqlite:///:memory:")
    time_service = TestingTime()

    simulation_service.run_migration()

    crypto_service = SimulatedCryptoService(simulation_service, time_service)

    return crypto_service
