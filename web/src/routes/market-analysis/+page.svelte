<script lang="ts">
    import Graph from "./graph.svelte";
    import Table from "./table.svelte";
    import type { PageData } from "./$types";

    export let data: PageData;
    const coinData = data.result;
</script>

<div>
    <Graph {coinData}></Graph>
    <Table {coinData}></Table>
</div>
