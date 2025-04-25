import {
    fetchNotifications
} from "./socket.js";


/** Sets up a visual element for the navigation showing which page the user is on. */
const setupMenuHighlighter = () => {
    const menuOptions = document.querySelectorAll(".nav-list-link");

    const highlightMenuOption = (selectedOption) => {
        menuOptions.forEach((option) => {
            if (option === selectedOption) {
                option.setAttribute("data-selected", "true");

                localStorage.setItem("selectedMenuOption", [...menuOptions].indexOf(option));
            } else {
                option.removeAttribute("data-selected");
            }
        });
    };

    const initializeHighlight = () => {
        const currentPath = window.location.pathname; // Get the current page's path
        let highlighted = false;

        // Match the current URL to the correct menu option
        menuOptions.forEach((option) => {
            const optionPath = new URL(option.href).pathname; // Get the href's path
            if (optionPath === currentPath) {
                highlightMenuOption(option);
                highlighted = true;
            }
        });

        // If no match is found, fall back to the saved state in localStorage
        if (!highlighted) {
            const savedIndex = localStorage.getItem("selectedMenuOption");
            if (savedIndex !== null) {
                const savedOption = menuOptions[parseInt(savedIndex, 10)];
                if (savedOption) {
                    highlightMenuOption(savedOption);
                }
            }
        }
    };

    // Initialize highlighting on page load
    initializeHighlight();

    // Set up click listeners for menu options
    menuOptions.forEach((option) => {
        option.addEventListener("click", () => {
            highlightMenuOption(option); // Save the state before navigation
        });
    });
};


/** Visual element for a menu toggle when the width of the screen goes below 1024 pixels.
 * Solves the problem of displaying the navigation on smaller screens.
 */
const setupMenuToggle = () => {
    const menuToggle = document.querySelector('.menu-toggle');
    const menuSection = document.querySelector('.menu-section');
    const notificationPanel = document.getElementById("notificationPanel");

    const updateMenuState = () => {
        if (window.innerWidth >= 1024) {
            menuSection.classList.remove('open'); // Ensure menu is visible
        }
    };

    // Add event listener for the toggle button
    menuToggle?.addEventListener('click', () => {
        if (window.innerWidth < 1024) {
            // Toggle the menu for small screens
            menuSection.classList.toggle('open');

            if (notificationPanel.style.right === "0px") {
            // Close the panel
            notificationPanel.style.right = "-350px";
            }
        }
    });

    // Update menu state on window resize
    window.addEventListener('resize', updateMenuState);

    // Set the initial state on page load
    updateMenuState();
}

/** Sets up a notification toggle for notification panel. */
const setupNotificationToggle = () => {
    const notificationPanel = document.getElementById("notificationPanel");
    const toggleButton = document.getElementById("toggleNotifications");
    const closeButton = document.getElementById("closeNotifications");
    const clearAll = document.getElementById("clearAll");
    const menuSection = document.querySelector('.menu-section');

    // Show the notification panel
    toggleButton.addEventListener("click", function (event) {
        // event.preventDefault(); // Prevent default link behavior
        // notificationPanel.classList.add("active");

        if (notificationPanel.style.right === "0px") {
            // Close the panel
            notificationPanel.style.right = "-350px";
        } else {
            // Open the panel
            notificationPanel.style.right = "0px";
            fetchNotifications();

            if (window.innerWidth < 1024) {
                menuSection.classList.remove('open');
            }
        }
    });

    // Hide the notification panel
    closeButton.addEventListener("click", function () {
        if (notificationPanel.style.right === "0px") {
            notificationPanel.style.right = "-350px";
        }
        // notificationPanel.classList.remove("active");
    });

    // Clear all notifications button
    clearAll.addEventListener("click", function () {
        // let list = document.getElementById("notification-list");
        // while (list.firstChild) {
        //     list.removeChild(list.firstChild);
        // }
        document.getElementById("notification-list").innerHTML = "";
        fetch('/notification_clear', {
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

    // Close the panel if user clicks outside of it
    document.addEventListener("click", function (event) {
        if (!notificationPanel.contains(event.target) && event.target !== toggleButton) {
            notificationPanel.classList.remove("active");
        }
    });
}

export {
    setupMenuHighlighter,
    setupMenuToggle,
    setupNotificationToggle
};