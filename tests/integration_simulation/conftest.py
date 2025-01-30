import pytest

from investorbot.enums import AppIntegration
from investorbot.integrations.simulation.providers import (
    DataProvider,
    StaticTimeProvider,
)
from investorbot.integrations.simulation.services import (
    SimulatedCryptoService,
    SimulationService,
)


@pytest.fixture(autouse=True)
def set_environment(monkeypatch):
    monkeypatch.setattr(
        "investorbot.INVESTOR_APP_INTEGRATION",
        str(AppIntegration.SIMULATED),
    )


@pytest.fixture
def mock_simulated_crypto_service(monkeypatch) -> SimulatedCryptoService:
    monkeypatch.setattr(
        "investorbot.integrations.simulation.providers.TIME_SERIES_DATA_PATH",
        "./tests/integration_simulation/fixtures/simulation.csv",
    )

    simulation_service = SimulationService("sqlite:///:memory:")
    time_service = StaticTimeProvider()
    data_provider = DataProvider(time_service)

    simulation_service.run_migration()

    crypto_service = SimulatedCryptoService(simulation_service, data_provider)

    return crypto_service
