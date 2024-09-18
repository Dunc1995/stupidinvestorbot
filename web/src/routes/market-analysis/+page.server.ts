import type { PageServerLoad } from './$types';
import { dbClient } from '$lib/db';
import { marketAnalysis } from '$lib/schema';
import { desc } from 'drizzle-orm';

export const load = (async () => {
    const result = await dbClient.query.marketAnalysis.findFirst({
        orderBy: desc(marketAnalysis.marketAnalysisId),
        with: {
            timeSeriesSummary: true,
            rating: true
        },
    });

    return { result: result };
}) satisfies PageServerLoad;