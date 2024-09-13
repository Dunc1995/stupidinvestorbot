import { integer, numeric, sqliteTable, text, } from "drizzle-orm/sqlite-core";

export const coinProperties = sqliteTable('coin_properties', {
    coinName: text('coin_name'),
    quantityTickSize: numeric('quantity_tick_size'),
    quantityDecimals: numeric('quantity_decimals'),
    priceTickSize: numeric('price_tick_size'),
    priceDecimals: numeric('price_decimals')
});


export const timeSeriesSummary = sqliteTable('time_series_data', {
    summaryId: integer('summary_id'),
    coinName: text('coin_name'),
    mean: numeric('mean'),
    std: numeric('std'),
    percentageStd: numeric('percentage_std'),
    lineOfBestFitCoefficient: numeric('line_of_best_fit_coefficient'),
    lineOfBestFitOffset: numeric('line_of_best_fit_offset'),
    value24HoursAgo: numeric('value_24_hours_ago'),
    timeOffset: numeric('time_offset'),
    isOutlier: integer('is_outlier', { mode: 'boolean' }).notNull().default(false),
    marketAnalysisId: integer('market_analysis_id')
})

export type timeSeriesSummary = typeof timeSeriesSummary.$inferSelect;