<script lang="ts">
    import type { TableRow } from "$lib/types";
    import type { Chart } from "chart.js";
    import ControlPanelCheckbox from "./ControlPanelCheckbox.svelte";
    import FilterIcon from "./FilterIcon.svelte";

    export let coinData: TableRow[];
    export let chartData: Chart | undefined;

    let isDisplayAllChecked = true;
    let isFallingChecked = false;
    let isFallingNominalChecked = false;
    let isFallingOutlierChecked = false;
    let isRisingChecked = false;
    let isRisingNominalChecked = false;
    let isRisingOutlierChecked = false;
    let isOutlierChecked = false;
    let isNotOutlierChecked = false;
</script>

<div class="dropdown dropdown-end float-right">
    {#if chartData}
        <div role="button" tabindex="0" class="btn m-1">
            <FilterIcon /> Filters
        </div>
        <ul
            class="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
            tabindex="-1"
        >
            <li>
                <ControlPanelCheckbox
                    labelName="Display All"
                    bind:isChecked={isDisplayAllChecked}
                    bind:coinData
                    bind:chartData
                ></ControlPanelCheckbox>
            </li>
            <li>
                <ControlPanelCheckbox
                    labelName="Show Outliers"
                    propertyToToggle="isOutlier"
                    bind:isChecked={isOutlierChecked}
                    bind:coinData
                    bind:chartData
                ></ControlPanelCheckbox>
            </li>
            <li>
                <ControlPanelCheckbox
                    labelName="Hide Outliers"
                    propertyToToggle="isOutlier"
                    invert={true}
                    bind:isChecked={isNotOutlierChecked}
                    bind:coinData
                    bind:chartData
                ></ControlPanelCheckbox>
            </li>
            <li>
                <ControlPanelCheckbox
                    labelName="All Rising Trends"
                    propertyToToggle="isRising"
                    bind:isChecked={isRisingChecked}
                    bind:coinData
                    bind:chartData
                ></ControlPanelCheckbox>
            </li>
            <li>
                <ControlPanelCheckbox
                    labelName="Rising Nominal Trends"
                    propertyToToggle="isRisingNominal"
                    bind:isChecked={isRisingNominalChecked}
                    bind:coinData
                    bind:chartData
                ></ControlPanelCheckbox>
            </li>
            <li>
                <ControlPanelCheckbox
                    labelName="Rising Outlier Trends"
                    propertyToToggle="isRisingOutlier"
                    bind:isChecked={isRisingOutlierChecked}
                    bind:coinData
                    bind:chartData
                ></ControlPanelCheckbox>
            </li>
            <li>
                <ControlPanelCheckbox
                    labelName="All Fallings Trends"
                    propertyToToggle="isFalling"
                    bind:isChecked={isFallingChecked}
                    bind:coinData
                    bind:chartData
                ></ControlPanelCheckbox>
            </li>
            <li>
                <ControlPanelCheckbox
                    labelName="Falling Nominal Trends"
                    propertyToToggle="isFallingNominal"
                    bind:isChecked={isFallingNominalChecked}
                    bind:coinData
                    bind:chartData
                ></ControlPanelCheckbox>
            </li>
            <li>
                <ControlPanelCheckbox
                    labelName="Falling Outlier Trends"
                    propertyToToggle="isFallingOutlier"
                    bind:isChecked={isFallingOutlierChecked}
                    bind:coinData
                    bind:chartData
                ></ControlPanelCheckbox>
            </li>
        </ul>
    {:else}
        <div role="button" class="btn m-1">
            <FilterIcon />
            <span class="loading loading-dots loading-md"></span>
        </div>
        <ul
            class="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
        ></ul>
    {/if}
</div>
