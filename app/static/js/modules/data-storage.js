/**
 * Stores relevant data in the arrays needed for chart.js chart.
 *
 * @type {{ sensorData: {}; temperatureData: {}; humidityData: {}; timestamps: {}; fetchInterval: any; paused: boolean; }}
 */
const dataStorage = {
    sensorData: [],
    temperatureData: [],
    humidityData: [],
    timestamps: [],
    fetchInterval: null,
    paused: false,
    selectedDevice: "",
};

export default dataStorage;