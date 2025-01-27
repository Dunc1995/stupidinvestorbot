def test_get_coin_balance_returns_latest_entry(mock_simulated_crypto_service):

    balance = mock_simulated_crypto_service.get_coin_balance("USD")

    assert balance.market_value == 120.0
