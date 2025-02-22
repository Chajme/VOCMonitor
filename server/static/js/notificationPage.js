import {
    fetchNotifications
} from "./modules/socket.js";

import {
    setupMenuHighlighter,
    setupMenuToggle
} from "./modules/visualElements.js";

document.addEventListener('DOMContentLoaded', function () {

    setupMenuHighlighter();
    setupMenuToggle();

    fetchNotifications();

    setInterval(fetchNotifications, 10000);

    const notificationPanel = document.getElementById("notificationPanel");
    const toggleButton = document.getElementById("toggleNotifications");
    const closeButton = document.getElementById("closeNotifications");

    // Show the notification panel
    toggleButton.addEventListener("click", function (event) {
        // event.preventDefault(); // Prevent default link behavior
        // notificationPanel.classList.add("active");

        if (notificationPanel.style.right === "0px") {
            // Close the panel
            notificationPanel.style.right = "-350px"; // Move the panel off-screen
        } else {
            // Open the panel
            notificationPanel.style.right = "0px";  // Move the panel into view
        }
    });

    // Hide the notification panel
    closeButton.addEventListener("click", function () {
        if (notificationPanel.style.right === "0px") {
            // Close the panel
            notificationPanel.style.right = "-350px";
        }
        // notificationPanel.classList.remove("active");
    });

    // Close the panel if user clicks outside of it
    document.addEventListener("click", function (event) {
        if (!notificationPanel.contains(event.target) && event.target !== toggleButton) {
            notificationPanel.classList.remove("active");
        }
    });
});