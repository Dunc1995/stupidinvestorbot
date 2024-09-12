from dataclasses import dataclass
import datetime
from typing import List
from investorbot.models import MarketAnalysis, TimeSeriesSummary
from web.decorators import format_date, format_numeric


@dataclass(init=False)
class TimeSeriesSummaryViewModel:
    summary_id: int
    coin_name: str
    value_offset: float
    is_outlier: bool
    __percentage_std: float
    __line_of_best_fit_coefficient: float

    @property
    @format_numeric(precision=2)
    def percentage_std(self) -> float:
        return self.__percentage_std * 100

    @property
    @format_numeric(precision=5)
    def line_of_best_fit_coefficient(self) -> float:
        return self.__line_of_best_fit_coefficient

    def __init__(self, ts_summary: TimeSeriesSummary):
        self.summary_id = ts_summary.summary_id
        self.coin_name = ts_summary.coin_name
        self.value_offset = ts_summary.value_24_hours_ago
        self.is_outlier = ts_summary.is_outlier
        self.__percentage_std = ts_summary.percentage_std
        self.__line_of_best_fit_coefficient = (
            ts_summary.normalized_line_of_best_fit_coefficient
        )


@dataclass(init=False)
class MarketAnalysisViewModel:
    __timestamp: int
    confidence_description: str
    requires_update: str
    ts_data: List[TimeSeriesSummaryViewModel]

    @property
    @format_date
    def creation_date(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.__timestamp / 1000)

    def __init__(self, market_analysis: MarketAnalysis, requires_update: bool):
        self.__timestamp = market_analysis.creation_time_ms
        self.confidence_description = market_analysis.rating.rating_description
        self.requires_update = "Yes" if requires_update else "No"
        self.ts_data = [
            TimeSeriesSummaryViewModel(ts_data) for ts_data in market_analysis.ts_data
        ]
