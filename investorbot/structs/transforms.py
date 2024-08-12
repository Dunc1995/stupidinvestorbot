from typing import List
from investorbot.structs.ingress import InstrumentJson
from investorbot.models import CoinProperties


def get_value_ratio(hours_since_order: float) -> float:
    return 0.98 + 0.03 ** ((0.01 * hours_since_order) + 1.0)


def get_coin_properties_from_instruments(
    instruments: List[InstrumentJson],
) -> List[CoinProperties]:
    return [
        CoinProperties(
            coin_name=instrument.symbol,
            quantity_tick_size=float(instrument.qty_tick_size),
            quantity_decimals=int(instrument.quantity_decimals),
            price_tick_size=float(instrument.price_tick_size),
            price_decimals=int(instrument.quote_decimals),
        )
        for instrument in instruments
    ]
