import type { PageServerLoad } from './$types';
import { coinProperties, dbClient } from '$lib/orm';

export const load = (async () => {
    const result = await dbClient.select().from(coinProperties).all();

    return { result: result };
}) satisfies PageServerLoad;