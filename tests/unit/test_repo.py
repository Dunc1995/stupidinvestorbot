INSTRUMENT_DATA = {
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

ORDER_DETAIL = {
    "id": 5,
    "method": "private/get-order-detail",
    "code": 0,
    "result": {
        "account_id": "32040f09-d4d6-43ba-9ae5-b6b4adabbb02",
        "order_id": "5755600402651476710",
        "client_oid": "00f73e67-fd02-4725-ba93-32fb59d0e2d6",
        "order_type": "LIMIT",
        "time_in_force": "GOOD_TILL_CANCEL",
        "side": "BUY",
        "exec_inst": [],
        "quantity": "0.90",
        "limit_price": "22.098",
        "order_value": "19.8882",
        "maker_fee_rate": "0",
        "taker_fee_rate": "0",
        "avg_price": "22.098",
        "ref_price": "0",
        "ref_price_type": "NULL_VAL",
        "cumulative_quantity": "0.90",
        "cumulative_value": "19.8882",
        "cumulative_fee": "0.0027",
        "status": "FILLED",
        "update_user_id": "32040f09-d4d6-43ba-9ae5-b6b4adabbb02",
        "order_date": "2024-08-09",
        "instrument_name": "AVAX_USD",
        "fee_instrument_name": "AVAX",
        "reason": 0,
        "create_time": 1723176268515,
        "create_time_ns": "1723176268515939076",
        "update_time": 1723176268516,
    },
}
