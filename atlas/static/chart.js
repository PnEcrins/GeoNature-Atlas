// ChartJS Graphs
const chartMainColor = getComputedStyle(document.documentElement).getPropertyValue('--main-color');
const chartSecondColor = getComputedStyle(document.documentElement).getPropertyValue('--second-color');
const chartThirdColor = getComputedStyle(document.documentElement).getPropertyValue('--third-color');

const getChartDatas = function (data, key) {
    let values = [];
    for (var i = 0; i < data.length; i++) {
        values.push(data[i][key])
    }
    return values
};

//Generic vertical bar graph
genericChart = function (element, labels, values) {
    return new Chart(element, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'observations',
                data: values,
                backgroundColor: chartMainColor,
                hoverBackgroundColor: chartSecondColor,
                borderWidth: 0
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    display: false
                },
            }
        }
    });
};

pieChartConfig = function (element, data) {
    return new Chart(element, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            cutout: "30%",
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: false
                }
            }
        }
    })
}

function getPieEndColor(index, isLastElem) {
    // To change color if last element will have the same color to first element
    if (isLastElem && index % 3 === 0) {
        index++
    }

    if (index % 3 === 0) {
        return chartMainColor
    } else if (index % 3 === 1) {
        return chartSecondColor
    }
    return chartThirdColor
}

function formatPieData(data) {
    let labels = []
    let data_count = []
    Object.keys(data).forEach(key => {
        labels.push(key)
        data_count.push(data[key])
    })

    return {
        labels: labels,
        datasets: [
            {
                label: `${translations.nb_observations} :`,
                data: data_count,
                backgroundColor: configuration.COLOR_PIE_CHARTS,
                hoverOffset: 25
            }
        ]
    }
}

var monthChartElement = document.getElementById('monthChart');
if (monthChartElement) {
    const monthChart = genericChart(monthChartElement, months_name, getChartDatas(months_value, 'value'));
}
var altiChartElement = document.getElementById('altiChart');
if (altiChartElement) {
    const altiChart = genericChart(altiChartElement, getChartDatas(dataset, 'altitude'), getChartDatas(dataset, 'value'));
}

const dataSourceChartElement = document.getElementById('organismChart');
if (dataSourceChartElement) {
    const organismChart = pieChartConfig(dataSourceChartElement, formatPieData(organism_stats));
}
