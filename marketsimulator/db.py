from marketsimulator import market_simulator_service
from marketsimulator.models import Instrument


BTC_DATA = {
    "symbol": "BTC_USD",
    "inst_type": "CCY_PAIR",
    "display_name": "BTC/USD",
    "base_ccy": "BTC",
    "quote_ccy": "USD",
    "quote_decimals": 2,
    "quantity_decimals": 5,
    "price_tick_size": "0.01",
    "qty_tick_size": "0.00001",
    "max_leverage": "50",
    "tradable": True,
    "expiry_timestamp_ms": 0,
    "beta_product": False,
    "margin_buy_enabled": True,
    "margin_sell_enabled": True,
}


def init_db():
    market_simulator_service.run_migration()

    btc_data = Instrument(**BTC_DATA)

    market_simulator_service.add_item(btc_data)
