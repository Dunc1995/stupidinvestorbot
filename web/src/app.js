import Chart from 'chart.js/auto'
import 'chartjs-adapter-date-fns';


const getRandomColour = () => {
    const red = Math.random() * 255.0;
    const green = Math.random() * 255.0;
    const blue = Math.random() * 255.0;

    return `rgb(${red}, ${green}, ${blue})`
}


const fetchData = async (coinName) => {
    const tsData = await fetch(`https://api.crypto.com/exchange/v1/public/get-valuations?instrument_name=${coinName}&valuation_type=mark_price&count=2880`)

    return tsData.json();
}

const getTimeSeriesData = async () => {
    let loader = document.getElementById("data-loading");
    let ctx = document.getElementById('graph-display');

    loader.style.display = "block";
    ctx.style.display = "none";

    let data = {
        datasets: []
    };

    await Promise.all(window.coinNames.map(async coinName => {
        let count = 0;
        tsData = await fetchData(coinName);

        truncatedData = [];

        tsDataRaw = tsData.result.data;

        firstEntry = tsDataRaw[tsDataRaw.length - 1]
        allData = tsDataRaw.map(dataPoint => { return { 'x': dataPoint.t, 'y': dataPoint.v / firstEntry.v } });

        for (let tsData of allData) {
            if (count % 20 === 0) {
                truncatedData.push(tsData);
            }
            count += 1;
        }

        const dataSeries = {
            label: coinName,
            data: truncatedData,
            borderColor: getRandomColour(),
            tension: 0.5
        };

        data.datasets.push(dataSeries)
    }));

    loader.style.display = "none";
    ctx.style.display = "block";

    return data;
}

function component(plotData) {
    const ctx = document.getElementById('graph-display');


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
                    borderWidth: 1
                },
                point: {
                    borderWidth: 0,
                    radius: 10,
                    backgroundColor: 'rgba(0,0,0,0)'
                }
            }
        }
    };

    new Chart(ctx, config);
}

window.onload = async function (e) {
    plotData = await getTimeSeriesData();

    component(plotData);
}