<script lang="ts">
    import type { PageData } from "./$types";

    export let data: PageData;
    let cashBalances = data.result;
</script>

<div class="container mx-auto pt-2 pb-2">
    <h1>Wallet Value History</h1>
    <ul>
        {#each cashBalances as cashBalance}
            <li>{cashBalance.value} - {cashBalance.creationTime}</li>
        {/each}
    </ul>
</div>
