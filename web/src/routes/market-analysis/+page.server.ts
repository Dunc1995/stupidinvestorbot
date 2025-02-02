import type { PageServerLoad } from './$types';
import { hostInternal } from '$lib/consts';
import type { MarketAnalysisContainer } from '$lib/types';

export const load = (async () => {
    const marketAnalysisResponse = await fetch(
        `${hostInternal}/get-market-analysis`,
    );


    const marketAnalysis: MarketAnalysisContainer = await marketAnalysisResponse.json()

    return {
        result: marketAnalysis
    };
}) satisfies PageServerLoad;