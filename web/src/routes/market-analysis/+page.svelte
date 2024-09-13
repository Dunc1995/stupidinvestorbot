<script lang="ts">
    import type { PageData } from "./$types";

    export let data: PageData;
</script>

<div>
    {#each data.result as coinProp}
        <h1>{coinProp.coinName}</h1>
    {/each}
</div>
