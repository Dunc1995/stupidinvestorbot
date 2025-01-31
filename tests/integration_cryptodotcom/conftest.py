import json
from typing import List
import pytest

from investorbot.enums import AppIntegration
from investorbot.context import BotContext
from investorbot.integrations.cryptodotcom.services import CryptoService
from investorbot.interfaces.services import ICryptoService


@pytest.fixture(autouse=True)
def set_environment(monkeypatch):
    monkeypatch.setattr(
        "investorbot.env.INVESTOR_APP_INTEGRATION",
        AppIntegration.CRYPTODOTCOM,
    )

    # ! Prevents test suite from attempting to write API response to api/** directory.
    monkeypatch.setattr(
        "investorbot.integrations.cryptodotcom.http.base.INVESTOR_APP_ENVIRONMENT",
        "Testing",
    )


def __get_file_data(filename: str) -> dict | List[dict]:
    example_data = None

    # TODO don't hardcode filepath
    with open(f"./tests/integration_cryptodotcom/fixtures/{filename}.json", "r") as f:
        example_data = json.loads(f.read())

    return example_data


@pytest.fixture
def get_file_data():

    return __get_file_data


@pytest.fixture
def mock_crypto_service() -> ICryptoService:
    crypto_service = CryptoService()
    crypto_service.user.api_key = "Test984bvwhibwbiytesTy"
    crypto_service.user.api_secret_key = "Test_ounghTtgwth874hWWWTESTG"

    return crypto_service


@pytest.fixture
def mock_context(mock_bot_db, mock_crypto_service):
    return BotContext(mock_bot_db, mock_crypto_service)
