export type TableRow = {
    isActive: boolean,
    data: TimeSeriesSummary
}

export type CashBalance = {
    cashBalanceId: number,
    usdBalance: number,
    totalEstimatedValueUsd: number,
    creationTime: Date
}

export type MarketAnalysis = {
    marketAnalysisId: number,
    confidenceRatingId: number,
    creationTimeMs: number
}

export type TimeSeriesSummary = {
    summaryId: number,
    coinName: string,
    mean: number,
    std: number,
    lineOfBestFitCoefficient: number,
    lineOfBestFitOffset: number,
    startingValue: number,
    datasetCount: number,
    timeOffset: number,
    isOutlierInGradient: boolean,
    isOutlierInOffset: boolean,
    isOutlierInDeviation: boolean,
    marketAnalysisId: number
}

export type CoinSelectionCriteria = {
    ratingId: number,
    ratingDescription: string,
}

export type MarketAnalysisContainer = {
    marketAnalysis: MarketAnalysis,
    coinSelectionCriteria: CoinSelectionCriteria,
    timeSeriesStatistics: TimeSeriesSummary[]
}