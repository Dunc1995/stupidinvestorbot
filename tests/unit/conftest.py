import pytest
from investorbot.integrations.simulation.providers import StaticTimeProvider


@pytest.fixture
def mock_time():
    return StaticTimeProvider()
