import json
import pytest

from investorbot.integrations.cryptodotcom import mappings
from investorbot.integrations.cryptodotcom.structs import InstrumentJson
from investorbot.services import AppService


@pytest.fixture
def mock_app_service():
    app_service = AppService("sqlite:///:memory:")
    app_service.run_migration()

    with open("./tests/integration/fixtures/get-instruments.json", "r") as f:
        instrument_data = json.loads(f.read())["result"]["data"]

    instruments = [InstrumentJson(**inst_data) for inst_data in instrument_data]
    coin_properties = [
        mappings.json_to_coin_properties(instrument) for instrument in instruments
    ]

    app_service.add_items(coin_properties)

    return app_service
