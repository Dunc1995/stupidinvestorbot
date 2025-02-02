<script lang="ts">
    import Graph from "$lib/components/Graph.svelte";
    import { getWalletGraphData } from "$lib/queries";
    import type { CashBalance } from "$lib/types";
    import type Chart from "chart.js/auto";
    import type { PageData } from "./$types";

    export let data: PageData;
    let walletBalances: CashBalance[] = data.result;
    let dataSource = getWalletGraphData(walletBalances);

    let chartData: Chart | undefined;
</script>

<div class="container mx-auto pt-2 pb-2">
    <h1>Wallet Value History</h1>
    <div class="flex w-full flex-col lg:flex-row">
        <div
            class="card bg-base-300 rounded-box grid h-32 flex-grow place-items-center"
        >
            content
        </div>
        <div class="divider lg:divider-horizontal"></div>
        <div
            class="card bg-base-300 rounded-box grid h-32 flex-grow place-items-center"
        >
            <Graph bind:dataSource bind:chartData isAsync={false}></Graph>
        </div>
    </div>
</div>
