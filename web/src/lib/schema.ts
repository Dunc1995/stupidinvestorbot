import { relations } from "drizzle-orm";
import { integer, numeric, sqliteTable, text, } from "drizzle-orm/sqlite-core";

export const coinProperties = sqliteTable('coin_properties', {
    coinName: text('coin_name'),
    quantityTickSize: numeric('quantity_tick_size'),
    quantityDecimals: numeric('quantity_decimals'),
    priceTickSize: numeric('price_tick_size'),
    priceDecimals: numeric('price_decimals')
});


export const coinSelectionCriteria = sqliteTable('coin_selection_criteria', {
    ratingId: integer('rating_id').primaryKey(),
    ratingDescription: text('rating_description'),
})


export const coinSelectionCriteriaRelations = relations(coinSelectionCriteria, ({ many }) => ({
    marketAnalyses: many(timeSeriesSummary),
}));


export const marketAnalysis = sqliteTable('market_analysis', {
    marketAnalysisId: integer('market_analysis_id').primaryKey(),
    confidenceRatingId: integer('confidence_rating_id'),
    creationTimeMs: integer('creation_time_ms')
})

export const marketAnalysisRelations = relations(marketAnalysis, ({ many, one }) => ({
    timeSeriesSummary: many(timeSeriesSummary),
    rating: one(coinSelectionCriteria, {
        fields: [marketAnalysis.confidenceRatingId],
        references: [coinSelectionCriteria.ratingId],
    })
}));

export const timeSeriesSummary = sqliteTable('time_series_data', {
    summaryId: integer('summary_id').primaryKey(),
    coinName: text('coin_name'),
    mean: numeric('mean'),
    std: numeric('std'),
    percentageStd: numeric('percentage_std'),
    lineOfBestFitCoefficient: numeric('line_of_best_fit_coefficient'),
    lineOfBestFitOffset: numeric('line_of_best_fit_offset'),
    startingValue: numeric('starting_value'),
    datasetCount: integer('dataset_count'),
    timeOffset: numeric('time_offset'),
    isOutlierInGradient: integer('is_outlier_in_gradient', { mode: 'boolean' }).notNull().default(false),
    isOutlierInOffset: integer('is_outlier_in_offset', { mode: 'boolean' }).notNull().default(false),
    isOutlierInDeviation: integer('is_outlier_in_deviation', { mode: 'boolean' }).notNull().default(false),
    marketAnalysisId: integer('market_analysis_id').references(() => marketAnalysis.marketAnalysisId)
})

export const timeSeriesSummaryRelations = relations(timeSeriesSummary, ({ one }) => ({
    marketAnalysis: one(marketAnalysis, {
        fields: [timeSeriesSummary.marketAnalysisId],
        references: [marketAnalysis.marketAnalysisId],
    }),
}));

export type marketAnalysis = typeof marketAnalysis.$inferSelect;
export type timeSeriesSummary = typeof timeSeriesSummary.$inferSelect;
export type coinSelectionCriteria = typeof coinSelectionCriteria.$inferSelect;