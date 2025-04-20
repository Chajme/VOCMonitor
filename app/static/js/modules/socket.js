/**
 * Defines a socket.
 */
const socket = io();


/**
 * Handles a notification permission.
 *
 * @param message
 */
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


/** Function to initialize WebSocket listeners */
function initializeSocket() {
    socket.on('alert', function(data) {
        console.log('Alert received:', data.message);
        handleNotification(data.message);
    });
}


/**
 * Function to fetch notification history from the db.
 *
 * @async
 */
async function fetchNotifications() {
    try {
        const response = await fetch('/notification_history');
        const data = await response.json();

        console.log('All database data:', data);

        const notificationList = document.getElementById('notification-list');
        notificationList.innerHTML = '';

        data.forEach(notification => {
            const listItem = document.createElement('li');
            listItem.setAttribute("data-id", notification.id);
            // listItem.textContent = notification.message;  // Correctly access message field



            listItem.innerHTML = `
                <strong>${notification.timestamp}</strong><br><br>
                ${notification.message} <br><br>
                <em>VOC Level: ${notification.voc}</em>
            `;

            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = 'X';
            deleteBtn.classList.add('delete-btn');

            // Check if ID exists before binding event
            if (notification.id) {
                deleteBtn.addEventListener('click', () => deleteNotification(notification.id));
            } else {
                console.error("Notification missing ID:", notification);
            }

            listItem.appendChild(deleteBtn);

            notificationList.appendChild(listItem);
        });

    } catch (error) {
        console.error('Error fetching all data:', error);
    }
}

// Ability to remove notifications one by one
window.deleteNotification = async function(id) {
    let response = await fetch('/delete_notification', {
        method: 'POST',
        headers: {'content-type': 'application/json'},
        body: JSON.stringify({id: id})
    });

    console.log("Notification id: ", id);

    let result = await response.json();
    if (response.ok && result.message === "Notification successfully deleted!") {
        fetchNotifications();
        document.querySelector(`#notification-list li[data-id='${id}']`)?.remove();
    } else {
        alert("Failed to delete notification.")
    }
}


export {
    initializeSocket,
    fetchNotifications
};