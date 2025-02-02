import type { PageServerLoad } from "../$types";
import type { TimeSeriesSummary } from "$lib/types";

export type CoinData = {
    coinName: string,
    history: TimeSeriesSummary[]
}

// TODO Implement API query
export const load = (async (pageData: any) => {
    console.log(pageData.params.slug)

    // const result = await dbClient.query.timeSeriesSummary.findMany({
    //     where: eq(timeSeriesSummary.coinName, pageData.params.slug),
    // });

    let coinData: CoinData = {
        coinName: pageData.params.slug,
        history: []
    }

    return { result: coinData };
}) satisfies PageServerLoad;
