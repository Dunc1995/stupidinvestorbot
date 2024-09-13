<script lang="ts">
    import Graph from "$lib/graph.svelte";
    import type { PageData } from "./$types";

    export let data: PageData;
</script>

<div>
    <!-- {#each data.result as coinProp}
        <h1>{coinProp.coinName}</h1>
        <p>{coinProp.mean}</p>
    {/each} -->
    <Graph coinData={data.result}></Graph>
</div>
