import { host } from "./consts";
import { getRandomColour } from "./graph";
import type { CashBalance, TableRow } from "./types";

const fetchData = async (coinName: string) => {
    const tsData = await fetch(
        `${host}/get-valuation?coin_name=${coinName}`
    );

    return tsData.json();
};

export const getTimeSeriesData = async (coinData: TableRow[]) => {
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
                coinName
            );
            let truncatedData = [];
            let tsDataRaw = tsData;

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

export const getCoinData = async (coinName: string) => {
    let count = 0;
    let data: any = {
        datasets: [],
    };

    const tsDataRaw = await fetchData(coinName)

    let truncatedData = [];

    let allData = tsDataRaw.map((dataPoint: any) => {
        return { x: dataPoint.t, y: dataPoint.v };
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
        borderColor: getRandomColour()
    };

    data.datasets.push(dataSeries);

    return data;
}

export const getWalletGraphData = (walletData: CashBalance[]) => {
    let data: any = {
        datasets: [],
    };


    let allData = walletData.map((dataPoint: CashBalance) => {
        return { x: dataPoint.creationTime, y: dataPoint.value };
    });

    const dataSeries = {
        label: "Wallet Value History",
        data: allData,
        borderColor: getRandomColour()
    };

    data.datasets.push(dataSeries);

    return data;
}