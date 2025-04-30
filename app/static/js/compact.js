import {
    fetchSensorData,
    fetchMinMaxValues,
    fetchAverages,
    updateChart,
    setCurrentState
} from "./modules/chart.js"

import {
    setupMenuHighlighter,
    setupMenuToggle,
    setupNotificationToggle
} from "./modules/visual-elements.js";

import {
    fetchUserSettingsJson
} from "./modules/settings-handler.js"

import {
    initializeSocket
} from "./modules/socket.js";

import dataStorage from "./modules/data-storage.js";

document.addEventListener('DOMContentLoaded', async () => {
    initializeSocket();
    setupMenuHighlighter();
    setupMenuToggle();
    setupNotificationToggle();

    // Waiting for user settings to get fetched, then setting the intervals
    const userSettingsJson = await fetchUserSettingsJson();
    fetchInterval = setInterval(() => {
        console.log('Calling fetchSensorData...');
        fetchSensorData(
            updateChart, setCurrentState, dataStorage.timestamps, dataStorage.sensorData, dataStorage.temperatureData, dataStorage.humidityData,
            userSettingsJson.advice1, userSettingsJson.advice2, userSettingsJson.advice3, userSettingsJson.advice4, userSettingsJson.advice5, userSettingsJson.advice6
        );
    }, userSettingsJson.fetch_sensor);

    setInterval(() => {
        fetchAverages();
    }, userSettingsJson.fetch_averages);

    setInterval(() => {
        fetchMinMaxValues();
    }, userSettingsJson.fetch_minmax);
});