<script lang="ts">
    import Graph from "./graph.svelte";
    import Table from "./table.svelte";
    import type { PageData } from "./$types";

    export let data: PageData;
</script>

<div>
    <Graph coinData={data.result}></Graph>
    <Table coinData={data.result}></Table>
</div>
