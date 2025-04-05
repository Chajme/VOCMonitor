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
    exportChartAsPNG,
    pauseFetchingHandler
} from "./modules/button-handlers.js";

import {
    setupMenuHighlighter,
    setupMenuToggle,
    setupNotificationToggle
} from "./modules/visual-elements.js";

import {
    fetchUserSettingsJson
} from "./modules/settings-handler.js";

import {
    fetchDevicesDropdown,
    fetchSelectedDevice
} from "./modules/devices-handler.js";

import dataStorage from "./modules/data-storage.js";

document.addEventListener('DOMContentLoaded', async () => {

    setupMenuHighlighter();
    setupMenuToggle();
    setupNotificationToggle();
    fetchSelectedDevice(dataStorage);

    // Setting up a chart and initializing it
    const ctx = document.getElementById('myChart').getContext('2d');
    const datasets = [
        {
            label: 'VOC Index',
            data: dataStorage.sensorData,
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
            data: dataStorage.temperatureData,
            borderWidth: 5,
            borderColor: '#ffa600',
            backgroundColor: '#ffa600',
            pointStyle: false,
        },
        {
            label: 'Humidity',
            data: dataStorage.humidityData,
            borderWidth: 5,
            borderColor: '#ff0000',
            backgroundColor: '#ff0000',
            pointStyle: false,
        },
    ];

    initChart(ctx, dataStorage.timestamps, datasets);
    attachEventHandlers(() => myChart.resetZoom());
    pauseFetchingHandler(() => {
        if (!dataStorage.paused) {
            console.log("Pausing fetching...");
            clearInterval(dataStorage.fetchInterval);
            dataStorage.fetchInterval = null;
        } else {
            console.log("Resuming fetching...");
            dataStorage.fetchInterval = setInterval(() => {
                fetchSensorData(
                    updateChart, setCurrentState, dataStorage.timestamps, dataStorage.sensorData, dataStorage.temperatureData, dataStorage.humidityData,
                    userSettingsJson.advice1, userSettingsJson.advice2, userSettingsJson.advice3,
                    userSettingsJson.advice4, userSettingsJson.advice5, userSettingsJson.advice6
                );
            }, userSettingsJson.fetch_sensor);
        }
        dataStorage.paused = !dataStorage.paused;
        console.log("Paused state is now:", dataStorage.paused);
    });

    document.getElementById('exportChartAsPDF').addEventListener('click', exportChartAsPDF);
    document.getElementById('exportChartAsPNG').addEventListener('click', exportChartAsPNG);
    document.getElementById('dropbtn').addEventListener('click', () => {
        fetchDevicesDropdown(clearDatasets, dataStorage);
    });

    document.getElementById('showAllData').addEventListener('change', async (event) => {
        if (event.target.checked) {
            myChart.data.labels.pop();
            await fetchAllData(updateChart);
            clearInterval(dataStorage.fetchInterval);
        } else {
            dataStorage.sensorData = [];
            dataStorage.temperatureData = [];
            dataStorage.humidityData = [];
            dataStorage.timestamps = [];

            updateChart(dataStorage.timestamps, dataStorage.sensorData, dataStorage.temperatureData, dataStorage.humidityData);

            dataStorage.fetchInterval = setInterval(() => {
                console.log('Calling fetchSensorData...');
                fetchSensorData(
                    updateChart, setCurrentState, dataStorage.timestamps, dataStorage.sensorData, dataStorage.temperatureData, dataStorage.humidityData,
                    userSettingsJson.advice1, userSettingsJson.advice2, userSettingsJson.advice3, userSettingsJson.advice4, userSettingsJson.advice5, userSettingsJson.advice6
                );
            }, userSettingsJson.fetch_sensor);
        }
    });

    // Waiting for user settings to get fetched, then setting the intervals
    const userSettingsJson = await fetchUserSettingsJson();
    dataStorage.fetchInterval = setInterval(() => {
        console.log('Calling fetchSensorData...');
        fetchSensorData(
            updateChart, setCurrentState, dataStorage.timestamps, dataStorage.sensorData, dataStorage.temperatureData, dataStorage.humidityData,
            userSettingsJson.advice1, userSettingsJson.advice2, userSettingsJson.advice3, userSettingsJson.advice4, userSettingsJson.advice5, userSettingsJson.advice6
        );
    }, userSettingsJson.fetch_sensor);
});

function clearDatasets() {
    dataStorage.sensorData.length = 0;
    dataStorage.temperatureData.length = 0;
    dataStorage.humidityData.length = 0;
    dataStorage.timestamps.length = 0;
    myChart.data.labels.pop();
    myChart.update();
}