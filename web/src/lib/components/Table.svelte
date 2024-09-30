<script lang="ts">
    import type { TableRow } from "$lib/types";

    export let coinData: TableRow[];
</script>

<h2>Statistics</h2>
<table class="table table-xs text-center text-wrap">
    <!-- head -->
    <thead>
        <tr>
            <th>Coin Name</th>
            <th>Normalized Gradient</th>
            <th>STD Outlier</th>
            <th>Gradient Outlier</th>
            <th>Offset Outlier</th>
        </tr>
    </thead>
    <tbody>
        {#each coinData as tableRow}
            <tr
                id={tableRow.data.coinName}
                class={tableRow.isActive ? "hover" : "text-neutral-400"}
            >
                <td
                    ><a href="/market-analysis/{tableRow.data.coinName}"
                        >{tableRow.data.coinName}</a
                    ></td
                >
                <td
                    >{(
                        Number(tableRow.data.lineOfBestFitCoefficient) /
                        Number(tableRow.data.value24HoursAgo)
                    ).toFixed(5)}</td
                >
                <td>{tableRow.data.isOutlierInDeviation}</td>
                <td>{tableRow.data.isOutlierInGradient}</td>
                <td>{tableRow.data.isOutlierInOffset}</td>
            </tr>
        {/each}
    </tbody>
</table>
