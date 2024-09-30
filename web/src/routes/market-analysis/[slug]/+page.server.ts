import { dbClient } from "$lib/db";
import { timeSeriesSummary } from "$lib/schema";
import { eq } from "drizzle-orm";
import type { PageServerLoad } from "../$types";

export type CoinData = {
    coinName: string,
    history: timeSeriesSummary[]
}

// TODO tidy this
export const load = (async (pageData: any) => {
    console.log(pageData.params.slug)

    const result = await dbClient.query.timeSeriesSummary.findMany({
        where: eq(timeSeriesSummary.coinName, pageData.params.slug),
    });

    let coinData: CoinData = {
        coinName: pageData.params.slug,
        history: result
    }

    return { result: coinData };
}) satisfies PageServerLoad;
