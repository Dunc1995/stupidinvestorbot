<script lang="ts">
    import type { TableRow } from "$lib/types";
    import type { Chart } from "chart.js";

    export let labelName: string;
    export let propertyToToggle: string = "";
    export let isChecked: boolean;
    export let coinData: TableRow[];
    export let chartData: Chart | undefined;

    const buttonToggle = (e: Event) => {
        if (!chartData) return;

        let target: HTMLInputElement = e.target as HTMLInputElement;

        isChecked = target.checked;

        chartData.config.data.datasets.map((graphData: any, index) => {
            let propertyToggle = propertyToToggle
                ? graphData[propertyToToggle]
                : true;

            let isVisible = isChecked && propertyToggle;

            chartData?.setDatasetVisibility(index, isVisible);

            let rowIndex = coinData.findIndex(
                (x) => x.data.summaryId === graphData.summaryId,
            );
            coinData[rowIndex].isActive = isVisible;
        });

        chartData.update();
    };
</script>

<div class="form-control p-0">
    <label class="label cursor-pointer">
        <input
            type="radio"
            name="radio-10"
            class="radio"
            checked={isChecked}
            on:change={buttonToggle}
        />
        <span class="label-text ml-2 mr-2">{labelName}</span>
    </label>
</div>
