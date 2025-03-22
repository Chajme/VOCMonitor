window.jsPDF = window.jspdf.jsPDF;

import {
    myChart,
    initChart,
    updateChart,
    fetchAllData,
    fetchSensorData,
    getGradient,
    fetchAverages,
    fetchMinMaxValues,
    setCurrentState
} from "./modules/chart.js";

import {
    attachEventHandlers,
    exportChartAsPDF,
    exportChartAsPNG,
    pauseFetchingHandler
} from "./modules/button-handlers.js";

import {
    initializeSocket
} from "./modules/socket.js";

import {
    setupMenuHighlighter,
    setupMenuToggle,
    setupNotificationToggle
} from "./modules/visual-elements.js";

import {
    fetchUserSettingsJson
} from "./modules/settings-handler.js"

import {
    fetchDevicesDropdown
} from "./modules/devices-handler.js"

let sensorData = [];
let temperatureData = [];
let humidityData = [];
let timestamps = [];
let fetchInterval;
let paused = false;

document.addEventListener('DOMContentLoaded', async () => {
    initializeSocket();
    setupMenuHighlighter();
    setupMenuToggle();
    setupNotificationToggle();

    const chartElement = document.getElementById('myChart');
    if (chartElement) {
        const ctx = chartElement.getContext('2d');
        // Setting up a chart and initializing it
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

        pauseFetchingHandler(() => {
            if (!paused) {
                console.log("Pausing fetching...");
                clearInterval(fetchInterval);
                fetchInterval = null;
            } else {
                console.log("Resuming fetching...");
                fetchInterval = setInterval(() => {
                    fetchSensorData(
                        updateChart, setCurrentState, timestamps, sensorData, temperatureData, humidityData,
                        userSettingsJson.advice1, userSettingsJson.advice2, userSettingsJson.advice3,
                        userSettingsJson.advice4, userSettingsJson.advice5, userSettingsJson.advice6
                    );
                }, userSettingsJson.fetch_sensor);
            }
            paused = !paused;
            console.log("Paused state is now:", paused);
        });

        // Export buttons listeners
        document.getElementById('exportChartAsPDF').addEventListener('click', exportChartAsPDF);
        document.getElementById('exportChartAsPNG').addEventListener('click', exportChartAsPNG);
        document.getElementById('dropbtn').addEventListener('click', () => {
            fetchDevicesDropdown(clearDatasets);
        });


        // ShowAllData button listener, stops fetching data when checked, displays all data from the database. Resumes fetching once unchecked
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
            console.log(userSettingsJson)
            fetchSensorData(
                updateChart, setCurrentState, timestamps, sensorData, temperatureData, humidityData,
                userSettingsJson.advice1, userSettingsJson.advice2, userSettingsJson.advice3, userSettingsJson.advice4, userSettingsJson.advice5, userSettingsJson.advice6
            );
        }, userSettingsJson.fetch_sensor);

        setInterval(() => {
            fetchAverages();
        }, userSettingsJson.fetch_averages);

        setInterval(() => {
            fetchMinMaxValues();
        }, userSettingsJson.fetch_minmax);
    }
});

function clearDatasets() {
    sensorData.length = 0;
    temperatureData.length = 0;
    humidityData.length = 0;
    timestamps.length = 0;
    myChart.data.labels.pop();
    myChart.update();
}