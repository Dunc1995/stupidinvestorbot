import json
from typing import List
import pytest

from investorbot.db import get_market_analysis_ratings
from investorbot.enums import AppIntegration
from investorbot.integrations.cryptodotcom import mappings
from investorbot.integrations.cryptodotcom.services import CryptoService
from investorbot.integrations.cryptodotcom.structs import InstrumentJson
from investorbot.interfaces.services import ICryptoService
from investorbot.services import AppService


@pytest.fixture(autouse=True)
def set_environment(monkeypatch):
    monkeypatch.setattr(
        "investorbot.INVESTOR_APP_INTEGRATION",
        str(AppIntegration.CRYPTODOTCOM),
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
