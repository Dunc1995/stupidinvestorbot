import Chart from 'chart.js/auto'
import 'chartjs-adapter-date-fns';


let graphSpinner = document.getElementById("data-loading");
let graphElement = document.getElementById('graph-display');
let isOutliersShown = true;
let outliersToggle = document.getElementById('toggle-outliers');


const getRandomColour = () => {
    const red = 60.0 + Math.random() * 195.0;
    const green = 60.0 + Math.random() * 195.0;
    const blue = 60.0 + Math.random() * 195.0;

    return `rgb(${red}, ${green}, ${blue})`
}


const fetchData = async (coinName) => {
    const tsData = await fetch(`https://api.crypto.com/exchange/v1/public/get-valuations?instrument_name=${coinName}&valuation_type=mark_price&count=2880`)

    return tsData.json();
}

const getTimeSeriesData = async () => {
    graphSpinner.style.display = "block";
    graphElement.style.display = "none";

    let data = {
        datasets: []
    };

    await Promise.all(window.coinData.map(async coinData => {
        let count = 0;
        const coinName = coinData['coin_name'];
        const isOutlier = coinData['is_outlier'];
        const valueOffset = coinData['value_offset'];

        let tsData = await fetchData(coinName);
        let truncatedData = [];
        let tsDataRaw = tsData.result.data;

        let allData = tsDataRaw.map(dataPoint => { return { 'x': dataPoint.t, 'y': dataPoint.v / valueOffset } });

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
            tension: isOutlier ? 0.1 : 0.5
        };

        data.datasets.push(dataSeries)
    }));

    graphSpinner.style.display = "none";
    graphElement.style.display = "block";

    return data;
}

const generateGraph = (plotData) => {
    const config = {
        type: 'line',
        data: plotData,
        options: {
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        boxWidth: 20
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    position: 'bottom'
                }
            },
            elements: {
                line: {
                    borderWidth: 1.5
                },
                point: {
                    borderWidth: 0,
                    radius: 10,
                    backgroundColor: 'rgba(0,0,0,0)'
                }
            }
        }
    };

    return new Chart(graphElement, config);
}


const toggleOutliers = (show) => {
    let chartData = window.chartData;

    chartData.config.data.datasets.map((graphData, index) => {
        if (graphData.isOutlier) {
            chartData.setDatasetVisibility(index, show)
        }
    })

    chartData.update();
}


window.onload = async function (e) {
    const graphData = await getTimeSeriesData();

    outliersToggle.innerHTML = "Hide Outliers";
    outliersToggle.disabled = false;

    window.chartData = generateGraph(graphData);

    outliersToggle.onclick = (e) => {
        let shown = !isOutliersShown

        outliersToggle.innerHTML = shown ? "Hide Outliers" : "Show Outliers";

        toggleOutliers(shown);

        isOutliersShown = shown;
    }
}