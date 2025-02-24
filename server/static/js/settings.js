import {
    fetchUserSettings,
    submitForms,
    cancelChanges,
    resetDefault} from "./modules/settingsHandler.js"

import {
    setupMenuHighlighter,
    setupMenuToggle,
    setupNotificationToggle
} from "./modules/visualElements.js";

document.addEventListener('DOMContentLoaded', () => {

    // Fetches current user settings to get displayed.
    fetchUserSettings();

    // Sets up visual elements
    setupMenuHighlighter();
    setupMenuToggle();
    setupNotificationToggle();

    // Button listeners for handling changes in settings
    document.getElementById('submitForms').addEventListener('click', submitForms);
    document.getElementById('cancelChanges').addEventListener('click', cancelChanges);
    document.getElementById('resetDefault').addEventListener('click', resetDefault);
});

