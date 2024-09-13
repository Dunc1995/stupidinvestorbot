import type { PageServerLoad } from './$types';
import { timeSeriesSummary } from '$lib/models';
import { dbClient } from '$lib/db';

export const load = (async () => {
    const result = await dbClient.select().from(timeSeriesSummary).all();

    return { result: result };
}) satisfies PageServerLoad;