from dataclasses import dataclass
from typing import List
from investorbot.models import TimeSeriesSummary
from web.decorators import format_numeric


@dataclass(init=False)
class TimeSeriesSummaryViewModel:
    summary_id: int
    coin_name: str
    __percentage_std: float
    __line_of_best_fit_coefficient: float
    __line_of_best_fit_offset: float

    @property
    @format_numeric(precision=2)
    def percentage_std(self) -> float:
        return self.__percentage_std * 100

    @property
    @format_numeric(precision=5)
    def line_of_best_fit_coefficient(self) -> float:
        return self.__line_of_best_fit_coefficient

    @property
    @format_numeric(precision=5)
    def line_of_best_fit_offset(self) -> float:
        return self.__line_of_best_fit_offset

    def __init__(self, ts_summary: TimeSeriesSummary):
        self.summary_id = ts_summary.summary_id
        self.coin_name = ts_summary.coin_name
        self.__percentage_std = ts_summary.percentage_std
        self.__line_of_best_fit_coefficient = ts_summary.line_of_best_fit_coefficient
        self.__line_of_best_fit_offset = ts_summary.line_of_best_fit_offset


@dataclass
class MarketAnalysisViewModel:
    ts_data: List[TimeSeriesSummaryViewModel]
