
import {
    setupMenuHighlighter,
    setupMenuToggle,
    setupNotificationToggle
} from "./modules/visual-elements.js";

import {
    addNewDevice,
    deleteDevice,
    fetchDevices,
    cancelChanges
} from "./modules/devices-handler.js";


document.addEventListener('DOMContentLoaded', async () => {
    setupMenuHighlighter();
    setupMenuToggle();
    setupNotificationToggle();

    fetchDevices();

    // Button listeners for handling changes in settings
    document.getElementById("addNewDevice").addEventListener("click", function (event) {
        event.preventDefault(); // Prevent form from submitting and refreshing
        const deviceName = document.getElementById("device_name").value;
        const topic = document.getElementById("topic").value;

        addNewDevice();

        console.log("Device Name:", deviceName);
        console.log("Topic:", topic);
    });
    document.getElementById('cancelChanges').addEventListener('click', cancelChanges);

    document.getElementById('clearAllDevices').addEventListener("click", function () {
        document.getElementById("devices-list").innerHTML = "";
        fetch('/devices_clear', {
            method: 'POST',
            body: JSON.stringify({}),
        })
            .then((response) => response.json())
            .then((data) => {
                alert(data.message);
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Failed to clear.');
            });
    });
});