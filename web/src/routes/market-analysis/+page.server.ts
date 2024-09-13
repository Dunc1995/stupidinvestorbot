import type { PageServerLoad } from './$types';
import { coinProperties } from '$lib/models';
import { dbClient } from '$lib/db';

export const load = (async () => {
    const result = await dbClient.select().from(coinProperties).all();

    return { result: result };
}) satisfies PageServerLoad;