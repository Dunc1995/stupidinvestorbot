import json
from typing import List
import pytest
import requests

from investorbot.db import get_market_analysis_ratings
from investorbot.integrations.cryptodotcom import mappings
from investorbot.integrations.cryptodotcom.structs import InstrumentJson
from investorbot.services import BotDbService


def __get_file_data(filename: str) -> dict | List[dict]:
    example_data = None

    # TODO don't hardcode filepath
    with open(f"./tests/fixtures/{filename}.json", "r") as f:
        example_data = json.loads(f.read())

    return example_data


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_call(*args, **kwargs):
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_call())
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: stunted_call())


@pytest.fixture
def mock_bot_db():
    bot_db = BotDbService("sqlite:///:memory:")
    bot_db.run_migration()

    instrument_data = __get_file_data("get-instruments")["result"]["data"]

    instruments = [InstrumentJson(**inst_data) for inst_data in instrument_data]
    coin_properties = [
        mappings.json_to_coin_properties(instrument) for instrument in instruments
    ]

    market_analysis_ratings = get_market_analysis_ratings()

    bot_db.add_items(coin_properties)
    bot_db.add_items(market_analysis_ratings)

    return bot_db
