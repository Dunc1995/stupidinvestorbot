import json
from typing import List
import pytest

from investorbot.db import get_market_analysis_ratings
from investorbot.integrations.cryptodotcom import mappings
from investorbot.integrations.cryptodotcom.services import CryptoService
from investorbot.integrations.cryptodotcom.structs import InstrumentJson
from investorbot.interfaces.services import ICryptoService
from investorbot.services import AppService
from investorbot.structs.internal import LatestTrade


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
def mock_app_service():
    app_service = AppService("sqlite:///:memory:")
    app_service.run_migration()

    instrument_data = __get_file_data("get-instruments")["result"]["data"]

    instruments = [InstrumentJson(**inst_data) for inst_data in instrument_data]
    coin_properties = [
        mappings.json_to_coin_properties(instrument) for instrument in instruments
    ]

    market_analysis_ratings = get_market_analysis_ratings()

    app_service.add_items(coin_properties)
    app_service.add_items(market_analysis_ratings)

    return app_service


@pytest.fixture
def mock_crypto_service() -> ICryptoService:
    crypto_service = CryptoService()
    crypto_service.user.api_key = "Test984bvwhibwbiytesTy"
    crypto_service.user.api_secret_key = "Test_ounghTtgwth874hWWWTESTG"

    return crypto_service
