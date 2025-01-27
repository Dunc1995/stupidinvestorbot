import pytest
import requests


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_call(*args, **kwargs):
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_call())
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: stunted_call())
