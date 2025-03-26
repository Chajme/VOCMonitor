/**
 * Messages for different voc thresholds.
 *
 * @type {*}
 */
let advice_1;
let advice_2;
let advice_3;
let advice_4;
let advice_5;
let advice_6;

/**
 * Fetching interval in ms.
 *
 * @type {*}
 */
let fetchSensorInterval;
let fetchAveragesInterval;
let fetchMinMaxInterval;
/**
 * Stores whether notifications are enabled.
 *
 * @type {*}
 */
let notificationsOn;
/**
 * Threshold for a notification.
 *
 * @type {*}
 */
let notificationsThreshold;
/**
 * Cooldown for notifications.
 *
 * @type {*}
 */
let notificationCooldown;
/**
 * Message that gets sent for a socket notification.
 *
 * @type {*}
 */
let notificationMessage;
/**
 * Email notifications enabled.
 *
 * @type {*}
 */
let emailNotificationOn;
/**
 * Threshold for email notifiations.
 *
 * @type {*}
 */
let emailNotificationThreshold;
/**
 * Cooldown for email notifications.
 *
 * @type {*}
 */
let emailNotificationCooldown;
/**
 * Email address.
 *
 * @type {*}
 */
let emailAddress;
/**
 * ESP alarm enabled.
 *
 * @type {*}
 */
let espAlarmEnabled;
/**
 * Length of time for the alarm in s.
 *
 * @type {*}
 */
let alarmTime;
/**
 * Temperature notifiactions enabled.
 *
 * @type {*}
 */
let tempNotificationsEnabled;
/**
 * Temperature notifications threshold.
 *
 * @type {*}
 */
let tempThreshold;
/**
 * Temperature notifications cooldown.
 *
 * @type {*}
 */
let tempCooldown;
/**
 * Humidity notifications enabled.
 *
 * @type {*}
 */
let humiNotificationsEnabled;
/**
 * Humidity threshold.
 *
 * @type {*}
 */
let humiThreshold;
/**
 * Humidity notifications cooldown.
 *
 * @type {*}
 */
let humiCooldown;


// Fetching user settings and setting variable values. Setting values to input fields.
async function fetchUserSettings() {
    fetch('/get_settings')
        .then(response => response.json())
        .then(data => {
            console.log(data);

            // Advice messages set for thresholds
            advice_1 = data.advice1;
            advice_2 = data.advice2;
            advice_3 = data.advice3;
            advice_4 = data.advice4;
            advice_5 = data.advice5;
            advice_6 = data.advice6;

            // Feteching
            fetchSensorInterval = data.fetch_sensor;
            fetchAveragesInterval = data.fetch_averages;
            fetchMinMaxInterval = data.fetch_minmax;

            // Socket notifications settings
            notificationsOn = data.notifications;
            notificationsThreshold = data.notification_threshold;
            notificationCooldown = data.cooldown;
            notificationMessage = data.notification_message;

            // Email notifications settings
            emailNotificationOn = data.email_notifications_on;
            emailNotificationThreshold = data.email_notification_threshold;
            emailNotificationCooldown = data.email_cooldown;
            emailAddress = data.email_address;

            // ESP32 alarm
            espAlarmEnabled = data.esp_alarm_enabled;
            alarmTime = data.alarm_time;

            // Temperature notifications
            tempNotificationsEnabled = data.temp_notifications_enabled;
            tempThreshold = data.temp_threshold;
            tempCooldown = data.temp_cooldown;

            // Humidity notifications
            humiNotificationsEnabled = data.humi_notifications_enabled;
            humiThreshold = data.humi_threshold;
            humiCooldown = data.humi_cooldown;

            // Assigning the values to elements
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

            document.getElementById('email-notifications-enabled').checked = emailNotificationOn;
            document.getElementById('email-notification-threshold').value = emailNotificationThreshold;
            document.getElementById('email-notification-cooldown').value = emailNotificationCooldown;
            document.getElementById('email-address').value = emailAddress;

            document.getElementById('esp-alarm-enabled').checked = espAlarmEnabled;
            document.getElementById('alarm-time').value = alarmTime;


            document.getElementById('temp-notifications-enabled').checked = tempNotificationsEnabled;
            document.getElementById('temp-threshold').value = tempThreshold;
            document.getElementById('temp-cooldown').value = tempCooldown;

            document.getElementById('humi-notifications-enabled').checked = humiNotificationsEnabled;
            document.getElementById('humi-threshold').value = humiThreshold;
            document.getElementById('humi-cooldown').value = humiCooldown;

        });
}


/**
 * // Fetching user settings, returning the fetched JSON.
 *
 * @async
 * @returns {response}
 */
async function fetchUserSettingsJson() {
    return fetch('/get_settings')
        .then((response)=>response.json())
        .then((responseJson)=>{return responseJson});
}


/** Handling information from all forms on the settings page. Sending it to the server and setting the changed user settings. */
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

    console.log(messagesForm);
    console.log(fetchingForm);
    console.log(notificationsForm);

    // Sends a message to the server to update the settings
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


/** Canceling the changes in the fields. Doesn't work when changes have been applied already. */
function cancelChanges() {
    fetchUserSettings();
}


/** Resetting the settings to default user settings  */
function resetDefault() {
    fetch('/default_settings', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({})
    })
        .then((response) => response.json())
        .then((data) => {
            alert(data.message);
            fetchUserSettings();
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Failed to reset settings.');
        });
}

export {
    fetchUserSettings,
    submitForms,
    cancelChanges,
    fetchUserSettingsJson,
    resetDefault
}