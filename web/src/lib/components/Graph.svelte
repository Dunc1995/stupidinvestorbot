<script lang="ts">
    import { onMount } from "svelte";
    import Chart from "chart.js/auto";
    import "chartjs-adapter-date-fns";
    import type { TableRow } from "$lib/types";

    export let coinData: TableRow[];
    export let chartData: Chart | undefined;
    let result: any;

    const getRandomColour = () => {
        const baseColour = 40.0;
        const colourVariability = 160.0;

        const red = baseColour + Math.random() * colourVariability;
        const green = baseColour + Math.random() * colourVariability;
        const blue = baseColour + Math.random() * colourVariability;

        return `rgb(${red}, ${green}, ${blue})`;
    };

    const fetchData = async (coinName: string, dataCount: number) => {
        const tsData = await fetch(
            `https://api.crypto.com/exchange/v1/public/get-valuations?instrument_name=${coinName}&valuation_type=mark_price&count=${dataCount}`,
        );

        return tsData.json();
    };

    const getTimeSeriesData = async () => {
        let data: any = {
            datasets: [],
        };

        await Promise.all(
            coinData.map(async (coinData) => {
                let rowData = coinData.data;

                let count = 0;
                const coinName = rowData.coinName ?? "";
                const isOutlier =
                    rowData.isOutlierInGradient ||
                    rowData.isOutlierInOffset ||
                    rowData.isOutlierInDeviation;
                const isRising =
                    Number(rowData.lineOfBestFitCoefficient) >= 0.0;
                const isFalling =
                    Number(rowData.lineOfBestFitCoefficient) < 0.0;

                const graphProperties = {
                    isRisingNominal: isRising && !isOutlier,
                    isRisingOutlier: isRising && isOutlier,
                    isFallingNominal: isFalling && !isOutlier,
                    isFallingOutlier: isFalling && isOutlier,
                };

                const valueOffset: any = rowData.startingValue;

                let tsData = await fetchData(
                    coinName,
                    rowData.datasetCount ?? 2880,
                );
                let truncatedData = [];
                let tsDataRaw = tsData.result.data;

                let allData = tsDataRaw.map((dataPoint: any) => {
                    return { x: dataPoint.t, y: dataPoint.v / valueOffset };
                });

                for (let tsDat of allData) {
                    if (count % 10 === 0) {
                        truncatedData.push(tsDat);
                    }
                    count += 1;
                }

                const dataSeries = {
                    summaryId: rowData.summaryId,
                    label: coinName,
                    data: truncatedData,
                    borderColor: getRandomColour(),
                    isOutlier: isOutlier,
                    isRising: isRising,
                    isFalling: isFalling,
                    borderDash: isOutlier ? [4, 4] : undefined,
                    tension: isOutlier ? 0.1 : 0.5,
                    ...graphProperties,
                };

                data.datasets.push(dataSeries);
            }),
        );

        return data;
    };

    const generateGraph = (canvasElement: HTMLCanvasElement): any => {
        const config: any = {
            type: "line",
            data: result,
            options: {
                plugins: {
                    legend: {
                        display: true,
                        position: "bottom",
                        labels: {
                            boxWidth: 20,
                        },
                    },
                },
                scales: {
                    x: {
                        type: "time",
                        position: "bottom",
                    },
                },
                elements: {
                    line: {
                        borderWidth: 1.5,
                    },
                    point: {
                        borderWidth: 0,
                        radius: 10,
                        backgroundColor: "rgba(0,0,0,0)",
                    },
                },
            },
        };

        const chart = new Chart(canvasElement, config);
        chart.destroy = chart.destroy.bind(chart);

        chartData = chart;
    };

    onMount(async (): Promise<any> => {
        result = await getTimeSeriesData();
    });
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
