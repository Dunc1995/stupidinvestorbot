<script lang="ts">
    import type { TableRow } from "$lib/types";

    export let coinData: TableRow[];

    console.log(coinData);
</script>

<h2>Statistics</h2>
<table class="table table-xs text-center text-wrap">
    <!-- head -->
    <thead>
        <tr>
            <th></th>
            <th>Coin Name</th>
            <th>Normalized Gradient</th>
            <th>Is Outlier in Gradient</th>
            <th>Is Outlier in Offset</th>
        </tr>
    </thead>
    <tbody>
        {#each coinData as tableRow}
            <tr class={tableRow.isActive ? "" : "text-neutral-400"}>
                <th>{tableRow.data.summaryId}</th>
                <td>{tableRow.data.coinName}</td>
                <td
                    >{(
                        Number(tableRow.data.lineOfBestFitCoefficient) /
                        Number(tableRow.data.value24HoursAgo)
                    ).toFixed(5)}</td
                >
                <td>{tableRow.data.isOutlierInGradient}</td>
                <td>{tableRow.data.isOutlierInOffset}</td>
            </tr>
        {/each}
    </tbody>
</table>
