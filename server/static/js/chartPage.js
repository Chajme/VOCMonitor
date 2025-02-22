import {
    myChart,
    initChart,
    updateChart,
    fetchAllData,
    fetchSensorData,
    getGradient,
    setCurrentState
} from "./modules/chart.js";

import {
    attachEventHandlers,
    exportChartAsPDF,
    exportChartAsPNG
} from "./modules/buttonHandlers.js";

import {
    setupMenuHighlighter,
    setupMenuToggle,
    setupNotificationToggle
} from "./modules/visualElements.js";

import {
    fetchUserSettingsJson
} from "./modules/settingsHandler.js";

document.addEventListener('DOMContentLoaded', async () => {
    var sensorData = [];
    var temperatureData = [];
    var humidityData = [];
    var timestamps = [];
    let fetchInterval;

    setupMenuHighlighter();
    setupMenuToggle();
    setupNotificationToggle();
    // initializeSocket();

    // Setting up a chart and initializing it
    const ctx = document.getElementById('myChart').getContext('2d');
    const datasets = [
        {
            label: 'VOC Index',
            data: sensorData,
            borderWidth: 5,
            borderColor: (context) => {
                const chart = context.chart;
                const { ctx, chartArea } = chart;
                if (!chartArea) return;
                return getGradient(ctx, chartArea);
            },
            backgroundColor: '#FFFFFF',
            pointStyle: false,
        },
        {
            label: 'Temperature',
            data: temperatureData,
            borderWidth: 5,
            borderColor: '#ffa600',
            backgroundColor: '#ffa600',
            pointStyle: false,
        },
        {
            label: 'Humidity',
            data: humidityData,
            borderWidth: 5,
            borderColor: '#ff0000',
            backgroundColor: '#ff0000',
            pointStyle: false,
        },
    ];

    initChart(ctx, timestamps, datasets);
    attachEventHandlers(() => myChart.resetZoom());

    document.getElementById('exportChartAsPDF').addEventListener('click', exportChartAsPDF);
    document.getElementById('exportChartAsPNG').addEventListener('click', exportChartAsPNG);

    document.getElementById('showAllData').addEventListener('change', async (event) => {
        if (event.target.checked) {
            myChart.data.labels.pop();
            await fetchAllData(updateChart);
            clearInterval(fetchInterval);
        } else {
            sensorData = [];
            temperatureData = [];
            humidityData = [];
            timestamps = [];

            updateChart(timestamps, sensorData, temperatureData, humidityData);

            // fetchInterval = setInterval(() => {
            //     console.log('Calling fetchSensorData...');
            //     fetchSensorData(updateChart, setCurrentState, timestamps, sensorData, temperatureData, humidityData);
            // }, 5000);

            fetchInterval = setInterval(() => {
                console.log('Calling fetchSensorData...');
                fetchSensorData(
                    updateChart, setCurrentState, timestamps, sensorData, temperatureData, humidityData,
                    userSettingsJson.advice1, userSettingsJson.advice2, userSettingsJson.advice3, userSettingsJson.advice4, userSettingsJson.advice5, userSettingsJson.advice6
                );
            }, userSettingsJson.fetch_sensor);
        }
    });

    // Waiting for user settings to get fetched, then setting the intervals
    const userSettingsJson = await fetchUserSettingsJson();
    fetchInterval = setInterval(() => {
        console.log('Calling fetchSensorData...');
        fetchSensorData(
            updateChart, setCurrentState, timestamps, sensorData, temperatureData, humidityData,
            userSettingsJson.advice1, userSettingsJson.advice2, userSettingsJson.advice3, userSettingsJson.advice4, userSettingsJson.advice5, userSettingsJson.advice6
        );
    }, userSettingsJson.fetch_sensor);



    // fetchInterval = setInterval(() => {
    //     console.log('Calling fetchSensorData...');
    //     fetchSensorData(updateChart, setCurrentState, timestamps, sensorData, temperatureData, humidityData);
    // }, 5000);

});