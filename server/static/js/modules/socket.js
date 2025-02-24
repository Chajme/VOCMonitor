
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
        const data = await response.json();

        console.log('All database data:', data);

        const notificationList = document.getElementById('notification-list');
        notificationList.innerHTML = '';

        data.forEach(notification => {
            const listItem = document.createElement('li');
            // listItem.textContent = notification.message;  // Correctly access message field

            // <button onclick="deleteNotification(${notification.id})" class="delete-btn">X</button>


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

// async function deleteNotification(id) {
//     let response = await fetch('/delete_notification', {
//         method: 'POST',
//         headers: {'content-type': 'application/json'},
//         body: JSON.stringify({id: id})
//     });

//     let result = await response.json();
//     if (result.success) {
//         fetchNotifications();
//     } else {
//         alert("Failed to delte notification.")
//     }
// }


export {
    initializeSocket,
    fetchNotifications
};