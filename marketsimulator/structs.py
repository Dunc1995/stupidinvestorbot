from dataclasses import dataclass


@dataclass
class ValuationDataInMemory:
    instrument_name: str
    t: int
    v: float
