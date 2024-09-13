<script lang="ts">
    import type { timeSeriesSummary } from "$lib/models";

    export let coinData: timeSeriesSummary[];
</script>

<div>
    <div class="collapse collapse-plus bg-base-200">
        <input type="checkbox" name="my-accordion-3" />
        <div class="collapse-title text-xl font-medium">Statistics</div>
        <div class="collapse-content">
            <div class="overflow-x-auto">
                <table class="table table-xs">
                    <!-- head -->
                    <thead>
                        <tr>
                            <th></th>
                            <th>Coin Name</th>
                            <th>Normalized Gradient</th>
                            <th>Is Outlier</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each coinData as coinDat}
                            <tr>
                                <th>{coinDat.summaryId}</th>
                                <td>{coinDat.coinName}</td>
                                <td
                                    >{(
                                        Number(
                                            coinDat.lineOfBestFitCoefficient,
                                        ) / Number(coinDat.value24HoursAgo)
                                    ).toFixed(5)}</td
                                >
                                <td>{coinDat.isOutlier}</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
