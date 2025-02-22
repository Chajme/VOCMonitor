let advice_1;
let advice_2;
let advice_3;
let advice_4;
let advice_5;
let advice_6;

let fetchSensorInterval;
let fetchAveragesInterval;
let fetchMinMaxInterval;
let notificationsOn;
let notificationsThreshold;
let notificationCooldown;
let notificationMessage;

// Fetching user settings and setting variable values. Setting values to input fields.
async function fetchUserSettings() {
    fetch('/get_settings')
        .then(response => response.json())
        .then(data => {
            console.log(data);

            advice_1 = data.advice1;
            advice_2 = data.advice2;
            advice_3 = data.advice3;
            advice_4 = data.advice4;
            advice_5 = data.advice5;
            advice_6 = data.advice6;

            fetchSensorInterval = data.fetch_sensor;
            fetchAveragesInterval = data.fetch_averages;
            fetchMinMaxInterval = data.fetch_minmax;

            notificationsOn = data.notifications;
            notificationsThreshold = data.notification_threshold;
            notificationCooldown = data.cooldown;
            notificationMessage = data.notification_message;

            document.getElementById('advice-1').value = advice_1;
            document.getElementById('advice-2').value = advice_2;
            document.getElementById('advice-3').value = advice_3;
            document.getElementById('advice-4').value = advice_4;
            document.getElementById('advice-5').value = advice_5;
            document.getElementById('advice-6').value = advice_6;

            document.getElementById('fetch-sensor').value = fetchSensorInterval;
            document.getElementById('fetch-averages').value = fetchAveragesInterval;
            document.getElementById('fetch-minmax').value = fetchMinMaxInterval;

            document.getElementById('notifications-enabled').checked = notificationsOn;
            document.getElementById('notification-threshold').value = notificationsThreshold;
            document.getElementById('notification-cooldown').value = notificationCooldown;
            document.getElementById('notification-message').value = notificationMessage;
        });
}

// Fetching user settings, returning the fetched JSON.
async function fetchUserSettingsJson() {
    return fetch('/get_settings')
        .then((response)=>response.json())
        .then((responseJson)=>{return responseJson});
}

async function populateFields() {
    if (document.body.contains(document.getElementById("settings-container"))) {
        document.getElementById('advice-1').value = advice_1;
        document.getElementById('advice-2').value = advice_2;
        document.getElementById('advice-3').value = advice_3;
        document.getElementById('advice-4').value = advice_4;
        document.getElementById('advice-5').value = advice_5;
        document.getElementById('advice-6').value = advice_6;

        document.getElementById('fetch-sensor').value = fetchSensorInterval;
        document.getElementById('fetch-averages').value = fetchAveragesInterval;
        document.getElementById('fetch-minmax').value = fetchMinMaxInterval;
        document.getElementById('notifications-enabled').checked = notificationsOn;
        document.getElementById('notification-threshold').value = notificationsThreshold;
        document.getElementById('notification-cooldown').value = notificationCooldown;
    }
}

// Handling information from all forms on the settings page. Sending it to the server and setting the changed user settings.
function submitForms() {
    const messagesForm = new FormData(document.getElementById('messages-form'));
    const fetchingForm = new FormData(document.getElementById('fetching-form'));
    const notificationsForm = new FormData(document.getElementById('notifications-form'));

    const formData = new URLSearchParams();

    for (const [key, value] of messagesForm) {
        formData.append(key, value);
    }
    for (const [key, value] of fetchingForm) {
        formData.append(key, value);
    }
    for (const [key, value] of notificationsForm) {
        formData.append(key, value === 'on' ? true : value);
    }

    // const idk = Array.from(document.querySelectorAll('#fetching-form input')).reduce((acc, input) =>
    //     ({...acc, [input.id]: input.value}), {}
    // );

    // console.log(idk);

    console.log(messagesForm);
    console.log(fetchingForm);
    console.log(notificationsForm);

    fetch('/update_settings', {
        method: 'POST',
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            alert(data.message);
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Failed to update settings.');
        });
}

// Canceling the changes in the fields. Doesn't work when changes have been applied already.
function cancelChanges() {
    fetchUserSettings();
}

export {
    fetchUserSettings,
    submitForms,
    cancelChanges,
    populateFields,
    fetchUserSettingsJson,
    advice_1,
    advice_2,
    advice_3,
    advice_4,
    advice_5,
    advice_6,
    fetchSensorInterval,
    fetchAveragesInterval,
    fetchMinMaxInterval,
    notificationsOn,
    notificationsThreshold,
    notificationCooldown,
    notificationMessage
}