<script lang="ts">
    import type { TableRow } from "$lib/types";
    import type { Chart } from "chart.js";
    import ControlPanelCheckbox from "./ControlPanelCheckbox.svelte";
    import GraphIcon from "./GraphIcon.svelte";
    import { afterUpdate, beforeUpdate } from "svelte";

    export let coinData: TableRow[];
    export let chartData: Chart | undefined;

    let isDisplayAllChecked = true;
    let isFallingChecked = false;
    let isRisingChecked = false;
    let isOutlierChecked = false;
</script>

{#if chartData}
    <details class="dropdown">
        <summary class="btn m-1"><GraphIcon />Controls</summary>
        <ul
            class="menu dropdown-content bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
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
    </details>
{:else}
    <details class="dropdown">
        <summary class="btn m-1">
            <GraphIcon />
            <span class="loading loading-dots loading-md"></span>
        </summary>
    </details>
{/if}
