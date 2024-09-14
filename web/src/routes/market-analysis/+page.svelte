<script lang="ts">
    import Graph from "./graph.svelte";
    import Table from "./table.svelte";
    import type { PageData } from "./$types";
    export let data: PageData;

    const coinData = data.result?.timeSeriesSummary;

    if (coinData === undefined)
        throw new ReferenceError("Time series analysis data was not found.");
</script>

<div class="flex w-full flex-col lg:flex-row">
    <div
        class="card bg-base-300 rounded-box grid h-200 p-2 flex-grow place-items-center"
    >
        <Graph {coinData}></Graph>
    </div>
    <div class="divider lg:divider-horizontal"></div>
    <div
        class="card bg-base-300 rounded-box grid h-200 p-2 flex-grow place-items-center overflow-x-auto"
    >
        <Table {coinData}></Table>
    </div>
</div>
