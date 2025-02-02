import type { PageServerLoad } from "../$types";

export type CoinData = {
    coinName: string,
}

export const load = (async (pageData: any) => {
    console.log(pageData.params.slug)

    let coinData: CoinData = {
        coinName: pageData.params.slug,
    }

    return { result: coinData };
}) satisfies PageServerLoad;
