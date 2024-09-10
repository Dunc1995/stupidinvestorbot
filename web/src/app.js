import Plotly from 'plotly.js-dist-min'

function component() {
    const tester = document.getElementById('tester');
    Plotly.newPlot(tester, [{
        x: [1, 2, 3, 4, 5],
        y: [1, 2, 4, 8, 16]
    }], {
        margin: { t: 0 }
    });
}

window.onload = function (e) {
    component();
}