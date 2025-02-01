from datetime import timedelta
import pytest

from investorbot.enums import AppIntegration
from investorbot.context import BotContext
from investorbot.providers import StaticTimeProvider
from investorbot.integrations.simulation.providers import (
    DataProvider,
    SimulatedTimeProvider,
)
from investorbot.integrations.simulation.services import (
    SimulatedCryptoService,
    SimulationDbService,
)


@pytest.fixture(autouse=True)
def set_environment(monkeypatch):
    monkeypatch.setattr(
        "investorbot.env.INVESTOR_APP_INTEGRATION",
        AppIntegration.SIMULATED,
    )


@pytest.fixture
def mock_simulated_crypto_service_with_data(
    monkeypatch, mock_simulated_time
) -> SimulatedCryptoService:

    simulation_db = SimulationDbService("sqlite:///:memory:")

    monkeypatch.setattr(
        "investorbot.integrations.simulation.providers.env.time",
        mock_simulated_time,
    )

    monkeypatch.setattr(
        "investorbot.integrations.simulation.services.env.time",
        mock_simulated_time,
    )

    data_provider = DataProvider(2000, generate_static_data=True)

    simulation_db.run_migration()

    crypto_service = SimulatedCryptoService(simulation_db, data_provider)

    return crypto_service


@pytest.fixture
def mock_simulated_crypto_service() -> SimulatedCryptoService:

    simulation_db = SimulationDbService("sqlite:///:memory:")

    data_provider = DataProvider(2000)

    simulation_db.run_migration()

    crypto_service = SimulatedCryptoService(simulation_db, data_provider)

    return crypto_service


@pytest.fixture
def mock_context(mock_bot_db, mock_simulated_crypto_service):
    return BotContext(mock_bot_db, mock_simulated_crypto_service)


@pytest.fixture
def mock_context_with_data(mock_bot_db, mock_simulated_crypto_service_with_data):
    return BotContext(mock_bot_db, mock_simulated_crypto_service_with_data)


@pytest.fixture
def mock_static_time() -> StaticTimeProvider:
    return StaticTimeProvider()


@pytest.fixture
def mock_simulated_time() -> SimulatedTimeProvider:
    return SimulatedTimeProvider(
        time_offset=timedelta(days=1), increment=timedelta(seconds=20)
    )
