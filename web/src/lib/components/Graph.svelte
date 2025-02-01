<script lang="ts">
    import { onMount } from "svelte";
    import Chart from "chart.js/auto";
    import "chartjs-adapter-date-fns";
    import { config } from "$lib/graph";

    export let chartData: Chart | undefined;
    export let dataSource: Promise<any> | any;
    export let isAsync: boolean = true;

    let result: any;

    const generateGraph = (canvasElement: HTMLCanvasElement): any => {
        let graphConfig = config;
        graphConfig.data = result;

        const chart = new Chart(canvasElement, config);
        chart.destroy = chart.destroy.bind(chart);

        chartData = chart;
    };

    if (isAsync) {
        onMount(async (): Promise<any> => {
            result = await dataSource;
        });
    } else {
        result = dataSource;
    }
</script>

{#if result}
    <canvas
        id="graph-display"
        class="rounded"
        style="width:500px;height:500px;"
        use:generateGraph
    ></canvas>
{:else}
    <span class="loading loading-ring loading-lg"></span>
{/if}
