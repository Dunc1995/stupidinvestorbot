<script lang="ts">
    import type Chart from "chart.js/auto";
    import type { PageData } from "./$types";
    import Graph from "$lib/components/Graph.svelte";
    import { getCoinData } from "$lib/queries";

    export let data: PageData;
    let coinData = data.result;

    let chartData: Chart | undefined;
    let dataSource = getCoinData(coinData.coinName);
</script>

<div>
    <h1>{coinData.coinName}</h1>
    <Graph bind:dataSource bind:chartData></Graph>
</div>
