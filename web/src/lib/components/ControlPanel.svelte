<script lang="ts">
    import type { TableRow } from "$lib/types";
    import type { Chart } from "chart.js";

    export let coinData: TableRow[];
    export let chartData: Chart | undefined;

    const buttonToggle = (
        initialMessage: string,
        altMessage: string,
        propertyToToggle: string,
        inverseProperty: boolean = false,
    ) => {
        return (e: MouseEvent) => {
            let target: HTMLButtonElement = e.target as HTMLButtonElement;

            if (!chartData) return;

            const toggleText = target.innerHTML === initialMessage;

            target.innerHTML = toggleText ? altMessage : initialMessage;

            chartData.config.data.datasets.map((graphData: any, index) => {
                let togglePropBool = graphData[propertyToToggle];

                const toggle: boolean = inverseProperty
                    ? !togglePropBool
                    : togglePropBool;

                let isVisible = toggle || !toggleText;
                chartData?.setDatasetVisibility(index, isVisible);

                let rowIndex = coinData.findIndex(
                    (x) => x.data.summaryId === graphData.summaryId,
                );
                coinData[rowIndex].isActive = isVisible;
            });

            chartData.update();
        };
    };
</script>

<button
    class="btn btn-outline btn-sm btn-secondary"
    on:click={buttonToggle("Show Only Rising", "Show All", "isRising")}
    >Show Only Rising</button
>
<button
    class="btn btn-outline btn-sm btn-secondary"
    on:click={buttonToggle("Hide Outliers", "Show Outliers", "isOutlier", true)}
    >Hide Outliers</button
>
