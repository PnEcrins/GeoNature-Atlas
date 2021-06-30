// ChartJS Graphs

Chart.defaults.global.defaultFontSize = 12;
const chartMainColor = getComputedStyle(document.documentElement).getPropertyValue('--main-color');
const chartHoverMainColor = getComputedStyle(document.documentElement).getPropertyValue('--second-color');

const getChartDatas = function (data, key) {
    let values = [];
    for (var i = 0; i < data.length; i++) {
        values.push(data[i][key])
    }
    return values
};

genericChart = function (element, labels, values) {
    return new Chart(element, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'observations',
                data: values,
                backgroundColor: chartMainColor,
                hoverBackgroundColor: chartHoverMainColor,
                borderWidth: 0
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }],
                xAxes: [{
                    gridLines: {
                        display: false
                    }
                }]
            },
            maintainAspectRatio: false,
            legend: {
                display: false
            }
        }
    });
};


var monthChartElement = document.getElementById('monthChart');
const monthChart = genericChart(monthChartElement, getChartDatas(months, 'mois'), getChartDatas(months, 'value'));

var altiChartElement = document.getElementById('altiChart');
const altiChart = genericChart(altiChartElement, getChartDatas(dataset, 'altitude'), getChartDatas(dataset, 'value'));
