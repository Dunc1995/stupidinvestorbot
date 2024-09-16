<script lang="ts">
    import type { TableRow } from "$lib/types";
    import type { Chart } from "chart.js";
    import ControlPanelCheckbox from "./ControlPanelCheckbox.svelte";
    import FilterIcon from "./FilterIcon.svelte";

    export let coinData: TableRow[];
    export let chartData: Chart | undefined;

    let isDisplayAllChecked = true;
    let isFallingChecked = false;
    let isRisingChecked = false;
    let isOutlierChecked = false;
    let isNotOutlierChecked = false;
</script>

{#if chartData}
    <div class="dropdown">
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
                    labelName="Is Rising"
                    propertyToToggle="isRising"
                    bind:isChecked={isRisingChecked}
                    bind:coinData
                    bind:chartData
                ></ControlPanelCheckbox>
            </li>
            <li>
                <ControlPanelCheckbox
                    labelName="Is Falling"
                    propertyToToggle="isFalling"
                    bind:isChecked={isFallingChecked}
                    bind:coinData
                    bind:chartData
                ></ControlPanelCheckbox>
            </li>
        </ul>
    </div>
{:else}
    <div class="dropdown">
        <div role="button" class="btn m-1">
            <FilterIcon />
            <span class="loading loading-dots loading-md"></span>
        </div>
        <ul
            class="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
        ></ul>
    </div>
{/if}
