<script lang="ts">
    import Graph from "../../lib/components/Graph.svelte";
    import Table from "../../lib/components/Table.svelte";
    import ControlPanel from "$lib/components/ControlPanel.svelte";
    import type { PageData } from "./$types";
    import type Chart from "chart.js/auto";
    import type { TableRow } from "$lib/types";
    import type { marketAnalysis } from "$lib/schema";
    export let data: PageData;

    let marketAnalysis: marketAnalysis | undefined = data.result;
    let coinData: TableRow[] = data.result?.timeSeriesSummary.map((x) => {
        return {
            isActive: true,
            data: x,
        };
    }) as TableRow[];
    let chartData: Chart | undefined;

    if (coinData === undefined)
        throw new ReferenceError("Time series analysis data was not found.");
</script>

<div class="container mx-auto pt-2 pb-2">
    <article class="p-5 prose-sm">
        <h1>Market Analysis</h1>
        <p>
            Behind the scenes, a collection of python scripts perform data
            processing on the coins as shown below to collate statistical
            properties for each coin.
        </p>
        <p>
            This information is used to get a general yardstick measurement to
            try and predict which coins are most likely to increase in value in
            a short timeframe.
        </p>
    </article>
    <ControlPanel bind:coinData bind:chartData></ControlPanel>
    <div class="flex w-full flex-col lg:flex-row pt-2">
        <div
            class="card bg-base-300 rounded-box grid h-200 p-2 flex-grow place-items-center"
        >
            <Graph bind:coinData bind:chartData></Graph>
        </div>

        <div class="divider lg:divider-horizontal"></div>
        <div
            class="card bg-base-300 rounded-box grid h-200 p-2 flex-grow place-items-center overflow-x-auto"
        >
            <Table bind:coinData></Table>
        </div>
    </div>
</div>
