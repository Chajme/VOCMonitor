/**
 * Fetches all the currently added devices from the server.
 *
 * @async
 */
async function fetchDevices() {
    try {
        const response = await fetch('/devices_list');
        const data = await response.json();

        console.log('All database data:', data);

        const devicesList = document.getElementById('devices-list');
        devicesList.innerHTML = '';

        var count = 1;

        data.forEach(device => {
            const listItem = document.createElement('li');
            listItem.setAttribute("data-id", device.id);
            // listItem.textContent = notification.message;  // Correctly access message field

            listItem.innerHTML = `
                <strong>${count}</strong>
                <strong>${device.device_name}</strong>
                ${device.topic} <br>
            `;

            count++;

            const deleteDeviceBtn = document.createElement('button');
            deleteDeviceBtn.textContent = 'remove';
            deleteDeviceBtn.classList.add('delete-device-btn');

            // Check if ID exists before binding event
            if (device.id) {
                deleteDeviceBtn.addEventListener('click', () => deleteDevice(device.id, device.device_name, device.topic));
            } else {
                console.error("Device missing ID:", device);
            }

            listItem.appendChild(deleteDeviceBtn);

            devicesList.appendChild(listItem);
        });

    } catch (error) {
        console.error('Error fetching all data:', error);
    }
}

/**
 * Fetched all the devices stored in the db and displayes them in a dropdown.
 *
 * @async
 * @param callback
 * @param dataStorage
 */
async function fetchDevicesDropdown(callback, dataStorage) {
    try {
        const response = await fetch('/devices_list');
        const data = await response.json();

        console.log('All database data:', data);

        const devicesList = document.getElementById('devices-dropdown'); // Ensure correct ID
        devicesList.innerHTML = ''; // Clear previous items

        data.forEach(device => {
            const listItem = document.createElement('a');
            listItem.setAttribute("data-id", device.id);
            dataStorage.selectedDevice = device.device_name;
            listItem.textContent = device.device_name;

            // Make the whole <a> clickable
            listItem.addEventListener('click', () => {
                if (callback) callback();
                dataStorage.selectedDevice = device.device_name;
                document.getElementById("dropbtn").textContent = device.device_name;
                selectDevice(device.id, device.device_name, device.topic);
            });

            devicesList.appendChild(listItem);
        });

    } catch (error) {
        console.error('Error fetching devices:', error);
    }
}


/**
 * Ability to remove devices one by one.
 *
 * @async
 * @param id
 * @param device_name
 * @param topic
 */
async function deleteDevice(id, device_name, topic) {
    let response = await fetch('/delete_device', {
        method: 'POST',
        headers: {'content-type': 'application/json'},
        body: JSON.stringify({id: id, device_name: device_name, topic: topic})
    });

    console.log("Device id: ", id);

    let result = await response.json();
    if (response.ok && result.message === "Device successfully deleted!") {
        fetchDevices();
        document.querySelector(`#device-list li[data-id='${id}']`)?.remove();
    } else {
        alert("Failed to delete device.")
    }
}

/**
 * Ability to remove devices one by one.
 *
 * @async
 * @param id
 * @param device_name
 * @param topic
 */
async function selectDevice(id, device_name, topic) {
    let response = await fetch('/select_device', {
        method: 'POST',
        headers: {'content-type': 'application/json'},
        body: JSON.stringify({id: id, topic: topic, device_name: device_name})
    });

    // let result = await response.json();
    // if (response.ok && result.message === "Device successfully selected!") {
    //     console.log("Device selected...", result.error)
    // } else {
    //     alert("Failed to select the device.")
    // }
}

/**
 * Fetched the currently selected device from the server.
 *
 * @async
 * @param dataStorage
 * @returns
 */
async function fetchSelectedDevice(dataStorage) {
    const response = await fetch('/current_device');
    const data = await response.json();

    // dataStorage.selectedDevice = data.selected_device;
    document.getElementById('dropbtn').textContent = data.selected_device;
}


/** Adds a new devices both visually to the form and sents a request to the server with the device info to add the device to the db. */
function addNewDevice() {
    const devicesForm = new FormData(
        document.getElementById('devices-form')
    );

    const formData = new URLSearchParams();

    for (const [key, value] of devicesForm) {
        formData.append(key, value);
    }

    console.log(devicesForm);

    fetch('/new_device', {
        method: 'POST',
        body: formData
    })
        .then((response) => response.json())
        .then((data) => {
            alert(data.message);
            fetchDevices();
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Failed to add a new device.');
        });
}


/** Canceling the changes in the fields. Doesn't work when changes have been applied already. */
function cancelChanges() {
    fetchDevices();
}

export {
    addNewDevice,
    deleteDevice,
    fetchDevices,
    fetchDevicesDropdown,
    cancelChanges,
    fetchSelectedDevice
}