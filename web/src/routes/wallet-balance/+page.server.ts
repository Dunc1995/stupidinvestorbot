import type { CashBalance } from '$lib/types';
import type { PageServerLoad } from './$types';


export const load = (async () => {
    const balanceHistory = await fetch(
        `http://127.0.0.1:5000/get-balance-history`,
    );


    const balanceHistoryJson: CashBalance[] = await balanceHistory.json()

    return {
        result: balanceHistoryJson
    };
}) satisfies PageServerLoad;