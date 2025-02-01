export const config: any = {
    type: "line",
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

export const getRandomColour = () => {
    const baseColour = 40.0;
    const colourVariability = 160.0;

    const red = baseColour + Math.random() * colourVariability;
    const green = baseColour + Math.random() * colourVariability;
    const blue = baseColour + Math.random() * colourVariability;

    return `rgb(${red}, ${green}, ${blue})`;
};