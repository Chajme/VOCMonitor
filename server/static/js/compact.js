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
} from "./modules/visualElements.js";

import {
    fetchUserSettingsJson
} from "./modules/settingsHandler.js"

document.addEventListener('DOMContentLoaded', async () => {
    var sensorData = [];
    var temperatureData = [];
    var humidityData = [];
    var timestamps = [];
    let fetchInterval;

    setupMenuHighlighter();
    setupMenuToggle();
    setupNotificationToggle();

    // Waiting for user settings to get fetched, then setting the intervals
    const userSettingsJson = await fetchUserSettingsJson();
    fetchInterval = setInterval(() => {
        console.log('Calling fetchSensorData...');
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
});