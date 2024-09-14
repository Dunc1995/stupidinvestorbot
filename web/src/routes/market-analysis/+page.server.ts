import type { PageServerLoad } from './$types';
import { dbClient } from '$lib/db';

export const load = (async () => {
    const result = await dbClient.query.marketAnalysis.findFirst({
        with: {
            timeSeriesSummary: true,
        },
    });

    return { result: result };
}) satisfies PageServerLoad;