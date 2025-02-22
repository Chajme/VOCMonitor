
const socket = io();

// Function to handle notification logic
function handleNotification(message) {
    if (Notification.permission === 'granted') {
        new Notification(message);
    } else {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                new Notification(message);
            }
        });
    }
}

// Function to initialize WebSocket listeners
function initializeSocket() {
    socket.on('alert', function(data) {
        console.log('Alert received:', data.message);
        handleNotification(data.message);
    });
}

// Function to fetch notification history from the db
async function fetchNotifications() {
    try {
        const response = await fetch('/notification_history');
        const data = await response.json();  // This should now work correctly

        console.log('All database data:', data);

        const notificationList = document.getElementById('notification-list');
        notificationList.innerHTML = '';

        data.forEach(notification => {
            const listItem = document.createElement('li');
            // listItem.textContent = notification.message;  // Correctly access message field


            listItem.innerHTML = `
                <strong>${notification.timestamp}</strong><br><br>
                ${notification.message} <br><br>
                <em>VOC Level: ${notification.voc}</em>
            `;

            notificationList.appendChild(listItem);
        });

    } catch (error) {
        console.error('Error fetching all data:', error);
    }
}


export {
    initializeSocket,
    fetchNotifications
};