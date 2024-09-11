import Chart from 'chart.js/auto'
import 'chartjs-adapter-date-fns';


const getRandomColour = () => {
    const red = Math.random() * 255.0;
    const green = Math.random() * 255.0;
    const blue = Math.random() * 255.0;

    return `rgb(${red}, ${green}, ${blue})`
}


const fetchData = async (coinName) => {
    const tsData = await fetch(`https://api.crypto.com/exchange/v1/public/get-valuations?instrument_name=${coinName}&valuation_type=mark_price&count=4000`)

    return tsData.json();
}

const getTimeSeriesData = async () => {
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

        console.log(allData)


        for (let tsData of allData) {
            if (count % 20 === 0) {
                truncatedData.push(tsData);
            }
            count += 1;
        }

        console.log(truncatedData)

        const dataSeries = {
            label: coinName,
            data: truncatedData,
            borderColor: getRandomColour(),
            tension: 0.1
        };

        data.datasets.push(dataSeries)
    }));

    return data;
}

function component(plotData) {
    const ctx = document.getElementById('graph-display');


    const config = {
        type: 'line',
        data: plotData,
        options: {
            scales: {
                x: {
                    type: 'time',
                    position: 'bottom'
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