<script lang="ts">
    import { onMount } from "svelte";
    import type { timeSeriesSummary } from "../../lib/models";
    import Chart from "chart.js/auto";
    import "chartjs-adapter-date-fns";

    export let coinData: timeSeriesSummary[];
    let result: any;

    const getRandomColour = () => {
        const red = 60.0 + Math.random() * 195.0;
        const green = 60.0 + Math.random() * 195.0;
        const blue = 60.0 + Math.random() * 195.0;

        return `rgb(${red}, ${green}, ${blue})`;
    };

    const fetchData = async (coinName: string) => {
        const tsData = await fetch(
            `https://api.crypto.com/exchange/v1/public/get-valuations?instrument_name=${coinName}&valuation_type=mark_price&count=2880`,
        );

        return tsData.json();
    };

    const getTimeSeriesData = async () => {
        let data: any = {
            datasets: [],
        };

        await Promise.all(
            coinData.map(async (coinData) => {
                let count = 0;
                const coinName = coinData.coinName ?? "";
                const isOutlier =
                    coinData.isOutlierInGradient || coinData.isOutlierInOffset;
                const valueOffset: any = coinData.value24HoursAgo;

                let tsData = await fetchData(coinName);
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
                    label: coinName,
                    data: truncatedData,
                    borderColor: getRandomColour(),
                    isOutlier: isOutlier,
                    borderDash: isOutlier ? [4, 4] : undefined,
                    tension: isOutlier ? 0.1 : 0.5,
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

        return new Chart(canvasElement, config);
    };

    onMount(async (): Promise<any> => {
        result = await getTimeSeriesData();
    });
</script>

{#if result}
    <canvas
        id="graph-display"
        class="rounded"
        style="width:800px;height:500px;"
        use:generateGraph
    ></canvas>
{:else}
    <span class="loading loading-ring loading-lg"></span>
{/if}
