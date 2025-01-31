from datetime import timedelta
import pytest

from investorbot.enums import AppIntegration
from investorbot.context import BotContext
from investorbot.integrations.simulation.providers import (
    DataProvider,
    SimulatedTimeProvider,
    StaticTimeProvider,
)
from investorbot.integrations.simulation.services import (
    SimulatedCryptoService,
    SimulationDbService,
)


@pytest.fixture(autouse=True)
def set_environment(monkeypatch):
    monkeypatch.setattr(
        "investorbot.env.INVESTOR_APP_INTEGRATION",
        str(AppIntegration.SIMULATED),
    )


@pytest.fixture
def mock_simulated_crypto_service(monkeypatch) -> SimulatedCryptoService:
    monkeypatch.setattr(
        "investorbot.integrations.simulation.providers.TIME_SERIES_DATA_PATH",
        "./tests/integration_simulation/fixtures/simulation.csv",
    )

    simulation_db = SimulationDbService("sqlite:///:memory:")
    data_provider = DataProvider()

    simulation_db.run_migration()

    crypto_service = SimulatedCryptoService(simulation_db, data_provider)

    return crypto_service


@pytest.fixture
def mock_context(mock_bot_db, mock_simulated_crypto_service):
    return BotContext(mock_bot_db, mock_simulated_crypto_service)


@pytest.fixture
def mock_static_time() -> StaticTimeProvider:
    return StaticTimeProvider()


@pytest.fixture
def mock_simulated_time() -> SimulatedTimeProvider:
    return SimulatedTimeProvider(
        time_offset=timedelta(days=1), increment=timedelta(seconds=20)
    )
