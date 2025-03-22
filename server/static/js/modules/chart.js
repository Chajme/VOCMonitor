window.jsPDF = window.jspdf.jsPDF;

let myChart;
let gradient, width, height;

// chart initialization, passing labels, datasets and context.
function initChart(context, labels, datasets) {
    myChart = new Chart(context, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets,
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 500,
                    display: true,
                    title: {
                        display: true,
                        text: 'VOC, °C, %',
                    },
                },
                x: {
                    beginAtZero: true,
                    display: true,
                    title: {
                        display: true,
                        text: 'Time',
                    },
                    ticks: {
                        callback: function (val, index) {
                            return index % 4 === 0 ? this.getLabelForValue(val) : '';
                        },
                    },
                },
            },
            plugins: {
                zoom: {
                    zoom: {
                        wheel: { enabled: true },
                        pinch: { enabled: true },
                        mode: 'x',
                        limits: { x: { min: 0, max: 100 } },
                    },
                },
                legend: {
                    onClick: function (e, legendItem, legend) {
                        toggleDatasetVisibility(legendItem, legend.chart);
                    },
                },
            },
        },
    });
}

// Updating the chart datasets.
function updateChart(timestamps, sensorData, temperatureData, humidityData) {
    myChart.data.labels = timestamps;
    myChart.data.datasets[0].data = sensorData;
    myChart.data.datasets[1].data = temperatureData;
    myChart.data.datasets[2].data = humidityData;
    myChart.update();
}

// Changing the scales of the y-axis based on the selected dataset.
function toggleDatasetVisibility(legendItem, chart) {
    const index = legendItem.datasetIndex;
    const meta = chart.getDatasetMeta(index);
    meta.hidden = meta.hidden === null ? !chart.data.datasets[index].hidden : null;

    const maxValues = [500, 50, 100];
    let newMax = 0;
    let activeLabel = -1;

    chart.data.datasets.forEach((dataset, i) => {
        if (!chart.getDatasetMeta(i).hidden) {
            newMax = Math.max(newMax, maxValues[i]);
            activeIndices.push(i);
            activeLabel = i;
        }
    });

    chart.options.scales.y.max = newMax || 10;

    const axisTitles = [
        { x: 'Time', y: 'VOC Index' },       // Dataset 0
        { x: 'Time', y: 'Temperature (°C)' }, // Dataset 1
        { x: 'Time', y: 'Humidity (%)' }      // Dataset 2
    ];

    if (activeIndex !== -1) {
        chart.options.scales.y.title.text = axisTitles[activeIndex].y;
        chart.options.scales.x.title.text = axisTitles[activeIndex].x;
    } else {
        chart.options.scales.y.title.text = 'Y-Axis Label';
        chart.options.scales.x.title.text = 'X-Axis Label';
    }

    chart.update();
}

// Changing the colour of one dataset to reflect the values in colour.
function getGradient(ctx, chartArea) {
    const chartWidth = chartArea.right - chartArea.left;
    const chartHeight = chartArea.bottom - chartArea.top;
    if (!gradient || width !== chartWidth || height !== chartHeight) {
        width = chartWidth;
        height = chartHeight;
        gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
        gradient.addColorStop(0, 'rgb(75, 192, 192)');
        gradient.addColorStop(0.5, 'rgb(255, 205, 86)');
        gradient.addColorStop(1, 'rgb(255, 99, 132)');
    }

    return gradient;
}

// Fetching all data from the server and updating the chart. Function is used for displaying all data from the database.
async function fetchAllData(updateChart) {
    try {
        const response = await fetch('/all-data');
        const data = await response.json();

        console.log('All database data: ', data);

        const { voc_index, temperature, humidity, timestamp } = data;
        updateChart(timestamp, voc_index, temperature, humidity);
    } catch (error) {
        console.error('Error fetching all data:', error);
    }
}

// Fetching sensor data, function fetches the most recent data from the database.
async function fetchSensorData(
    updateChart, setCurrentState, sensorData, temperatureData, humidityData, timestamps,
    advice_1, advice_2, advice_3, advice_4, advice_5, advice_6
) {
    try {
        const response = await fetch('/data');
        const data = await response.json();

        // Checking the response from the server, displaying the error code and the message
        if (!response.ok) {
            throw new Error(`${response.status}: ${data.message}`);
        }

        console.log('Received data:', data);

        // Update arrays
        sensorData.push(data.voc_index);
        temperatureData.push(data.temperature);
        humidityData.push(data.humidity);
        timestamps.push(data.timestamp);

        if (document.getElementById('myChart')) {
            // Update chart with new data
            updateChart(timestamps, sensorData, temperatureData, humidityData);
        }

        if (document.getElementById('advice') != null) {
            getAdvice(data.voc_index, advice_1, advice_2, advice_3, advice_4, advice_5, advice_6);
            // Call setCurrentState to update state logic
            setCurrentState(data.voc_index);
        }

        if (document.getElementById('temperature') != null) {
            // Update HTML elements
            document.getElementById('temperature').innerHTML = `${data.temperature}°C`;
            document.getElementById('humidity').innerHTML = `${data.humidity}%`;
            document.getElementById('voc-index').innerHTML = data.voc_index;
        }
    } catch (error) {
        console.error('Error fetching sensor data:', error);
    }
}

// Fetches average data for the past 24h, 72h and 7d from the database.
async function fetchAverages() {
    try {
        const response = await fetch('/avg');
        const data = await response.json();

        if (!response.ok) {
            throw new Error(`${response.status}: ${data.message}`);
        }

        console.log('Received averages: ', data);

        document.getElementById('avg-24h').innerHTML = data.avg_24h;
        document.getElementById('avg-72h').innerHTML = data.avg_72h;
        document.getElementById('avg-7d').innerHTML = data.avg_7d;
    } catch (error) {
        console.error('Error fetching avg data:', error);
    }
}

// Fetches the min and max values for the past 24h and 72h.
async function fetchMinMaxValues() {
    try {
        const response = await fetch('/minmax');
        const data = await response.json();

        if (!response.ok) {
            throw new Error(`${response.status}: ${data.message}`);
        }

        console.log('Received minmax: ', data);

        document.getElementById('min-24h').innerHTML = data.min_24h;
        document.getElementById('max-24h').innerHTML = data.max_24h;
        document.getElementById('min-72h').innerHTML = data.min_72h;
        document.getElementById('max-72h').innerHTML = data.max_72h;
    } catch (error) {
        console.error('Error fetching minmax data:', error);
    }
}


function setupIntervals(fetchSensorInterval, fetchAveragesInterval, fetchMinMaxInterval) {
    if (fetchSensorInterval > 0 && fetchAveragesInterval > 0 && fetchMinMaxInterval > 0) {
        // Set the intervals once all values are valid
        console.log('Setting up intervals...');

        fetchInterval = setInterval(() => {
            console.log('Calling fetchSensorData...');
            fetchSensorData(updateChart, setCurrentState, timestamps, sensorData, temperatureData, humidityData);
        }, fetchSensorInterval);

        setInterval(() => {
            fetchAverages();
        }, fetchAveragesInterval);

        setInterval(() => {
            fetchMinMaxValues();
        }, fetchMinMaxInterval);
    } else {
        // Log and retry after a short delay
        console.log('Intervals not ready yet. Retrying...');
        setTimeout(() => {
            setupIntervals(fetchSensorInterval, fetchAveragesInterval, fetchMinMaxInterval);
        }, 1000);
    }
}

// Gives air rating based on the current VOC index value.
function setCurrentState(currentVOC) {
    if (currentVOC <= 50) {
        document.getElementById('recommendation').innerHTML = "Excellent";
    } else if (currentVOC > 50 && currentVOC <= 100) {
        document.getElementById('recommendation').innerHTML = "Good";
    } else if (currentVOC > 100 && currentVOC <= 200) {
        document.getElementById('recommendation').innerHTML = "Moderate";
    } else if (currentVOC > 200 && currentVOC <= 300) {
        document.getElementById('recommendation').innerHTML = "Poor";
    } else if (currentVOC > 300 && currentVOC <= 450) {
        document.getElementById('recommendation').innerHTML = "Bad";
    } else {
        document.getElementById('recommendation').innerHTML = "Hazardous";
    }
}

// Gives user set advice for different VOC thresholds.
function getAdvice(currentVOC, advice_1, advice_2, advice_3, advice_4, advice_5, advice_6) {
    if (currentVOC <= 50) {
        document.getElementById('advice').innerHTML =
        advice_1;
    } else if (currentVOC > 50 && currentVOC <= 100) {
        document.getElementById('advice').innerHTML =
        advice_2;
    } else if (currentVOC > 100 && currentVOC <= 200) {
        document.getElementById('advice').innerHTML =
        advice_3;
    } else if (currentVOC > 200 && currentVOC <= 300) {
        document.getElementById('advice').innerHTML =
        advice_4;
    } else if (currentVOC > 300 && currentVOC <= 450) {
        document.getElementById('advice').innerHTML =
        advice_5;
    } else {
        document.getElementById('advice').innerHTML =
        advice_6;
    }
}

export {
    myChart,
    initChart,
    updateChart,
    fetchAllData,
    fetchSensorData,
    getGradient,
    fetchAverages,
    fetchMinMaxValues,
    setCurrentState,
    setupIntervals
};