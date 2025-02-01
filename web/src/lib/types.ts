import type { timeSeriesSummary } from "./schema"

export type TableRow = {
    isActive: boolean,
    data: timeSeriesSummary
}

export type CashBalance = {
    cashBalanceId: number,
    value: number,
    creationTime: Date
}