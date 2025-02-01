import { host } from '$lib/consts';
import type { CashBalance } from '$lib/types';
import type { PageServerLoad } from './$types';


export const load = (async () => {
    const balanceHistory = await fetch(
        `${host}/get-balance-history`,
    );


    const balanceHistoryJson: CashBalance[] = await balanceHistory.json()

    return {
        result: balanceHistoryJson
    };
}) satisfies PageServerLoad;