import pytest
from investorbot.providers import StaticTimeProvider


@pytest.fixture
def mock_time():
    return StaticTimeProvider()
