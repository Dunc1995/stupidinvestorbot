<script lang="ts">
    import type { PageData } from "./$types";

    export let data: PageData;
    let coinData = data.result;

    console.log(data);
</script>

<div>
    <h1>{coinData.coinName}</h1>
    <ul>
        {#each coinData.history as coinAnalysis}
            <li>{coinAnalysis.lineOfBestFitCoefficient}</li>
        {/each}
    </ul>
</div>
