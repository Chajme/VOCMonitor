"""Modules stores routes used for webserver navigation and handling of requests."""

import datetime
import time

from flask import Blueprint, render_template, jsonify, request, current_app
from flask_mail import Message


class Routes:
    """Represents routes used by the server for navigation handling requests and handling notifications."""

    def __init__(self, db, mqtt, socketio, mail):
        """
        Constructor of the routes class.

        Takes db, mqtt, socketio and mail as parameters,
        defines routes as a blueprint and keeps track of notifications.
        """

        self.db = db
        self.mqtt = mqtt
        self.socketio = socketio
        self.mail = mail

        self.routes = Blueprint("routes", __name__)

        self.last_notification = 0
        self.notification_sent = False
        self.last_email_notification = 0
        self.email_notification_sent = False
        self.last_temp_notification = 0
        self.temp_notification_sent = False
        self.last_humi_notification = 0
        self.humi_notification_sent = False

        self.socket_connection_established = False

        self.selected_device = "esp"

        self.create_routes()

    def create_routes(self):
        """Function to create all defined routes, returns the defined routes."""

        @self.routes.route("/")
        def index():
            return render_template("index.html")

        @self.routes.route("/compact")
        def compact():
            return render_template("compact.html")

        @self.routes.route("/chart")
        def chart():
            return render_template("chart.html")

        @self.routes.route("/devices")
        def devices():
            return render_template("devices.html")

        @self.routes.route("/settings")
        def settings():
            return render_template("settings.html")

        @self.routes.route("/all-data")
        def all_data():
            """Sends all data from the db for the selected device."""

            all_data_row = self.db.get_all_rows(self.selected_device)

            all_data_list = {
                "timestamp": [row[0] for row in all_data_row],
                "temperature": [row[1] for row in all_data_row],
                "humidity": [row[2] for row in all_data_row],
                "voc_index": [row[3] for row in all_data_row],
            }

            data_json = jsonify(all_data_list)
            return data_json

        @self.routes.route("/data")
        def new_data():
            """Sends new data from the db and checks for notifications."""

            try:
                new_data_row = self.db.get_last_row(self.selected_device)

                # If there's no data in the db yet, throw a response with the code 404
                if not new_data_row:
                    return jsonify({"message": "No data available"}), 404

                new_data_list = {
                    "timestamp": new_data_row[0],
                    "temperature": new_data_row[1],
                    "humidity": new_data_row[2],
                    "voc_index": new_data_row[3],
                }

                # Getting the user set notification settings
                (
                    notifications_on,
                    notifications_threshold,
                    cooldown,
                    notification_message,
                    email_notifications_on,
                    email_notification_threshold,
                    email_cooldown,
                    esp_alarm_enabled,
                    alarm_time,
                    temp_notifications_enabled,
                    temp_threshold,
                    temp_cooldown,
                    humi_notifications_enabled,
                    humi_threshold,
                    humi_cooldown,
                ) = self.db.get_user_settings_notifications()

                # If notifications are on, pass the data from the db to check_sensor_data function
                if (
                    notifications_on
                    or email_notifications_on
                    or temp_notifications_enabled
                    or humi_notifications_enabled
                    and self.db.get_last_row(self.selected_device) is not None
                ):
                    self.check_sensor_data(
                        notifications_on,
                        email_notifications_on,
                        int(new_data_row[3]),
                        notifications_threshold,
                        cooldown,
                        notification_message,
                        1000,
                        email_notification_threshold,
                        esp_alarm_enabled,
                        alarm_time,
                        temp_notifications_enabled,
                        temp_threshold,
                        temp_cooldown,
                        humi_notifications_enabled,
                        humi_threshold,
                        humi_cooldown,
                        int(new_data_row[2]),
                        int(new_data_row[1]),
                    )
                    return jsonify(new_data_list), 200

            except Exception as e:
                return jsonify({"message": f"Error fetching new data: {str(e)}"}), 500

        @self.routes.route("/avg")
        def get_averages():
            """Sends averages from the db for the specified device and time."""

            try:
                avg_24h = self.db.get_avg("-24 hours", self.selected_device)
                avg_72h = self.db.get_avg("-72 hours", self.selected_device)
                avg_7d = self.db.get_avg("-7 days", self.selected_device)

                averages = {"avg_24h": avg_24h, "avg_72h": avg_72h, "avg_7d": avg_7d}
            except Exception as e:
                return jsonify({"message": f"Error fetching averages {e}"}), 500

            return jsonify(averages), 200

        @self.routes.route("/minmax")
        def get_min_max_voc():
            """Sends min and max value from the db for the specified device and time."""

            try:
                min_24h, max_24h = self.db.get_min_max(
                    "-24 hours", self.selected_device
                )
                min_72h, max_72h = self.db.get_min_max(
                    "-72 hours", self.selected_device
                )

                min_max_voc_list = {
                    "min_24h": min_24h,
                    "max_24h": max_24h,
                    "min_72h": min_72h,
                    "max_72h": max_72h,
                }

                if any(value is None for value in min_max_voc_list.values()):
                    return jsonify({"message": "No minmax data available"}), 404

            except Exception as e:
                return jsonify({"message": f"Error fetching minmax {e}"}), 500

            return jsonify(min_max_voc_list), 200

        @self.routes.route("/update_settings", methods=["POST"])
        def update_settings():
            """Updates user settings in the db."""

            try:
                # Advice settings
                advice_1 = request.form.get("advice_1")
                advice_2 = request.form.get("advice_2")
                advice_3 = request.form.get("advice_3")
                advice_4 = request.form.get("advice_4")
                advice_5 = request.form.get("advice_5")
                advice_6 = request.form.get("advice_6")

                # Fetching settings
                fetch_sensor = request.form.get("fetch_sensor")
                fetch_averages = request.form.get("fetch_averages")
                fetch_minmax = request.form.get("fetch_minmax")

                # Socket notifications settings
                notifications_enabled = (
                    request.form.get("notifications_enabled") == "true"
                )
                notification_threshold = request.form.get("notification_threshold")
                notification_cooldown = request.form.get("notification_cooldown")
                notification_message = request.form.get("notification_message")

                # Email notification settings
                email_notifications_enabled = (
                    request.form.get("email_notifications_enabled") == "true"
                )
                email_notification_threshold = request.form.get(
                    "email_notification_threshold"
                )
                email_notification_cooldown = request.form.get(
                    "email_notification_cooldown"
                )
                email_address = request.form.get("email_address")

                # Alarm notification settings
                esp_alarm_enabled = request.form.get("esp_alarm_enabled")
                alarm_time = request.form.get("alarm_time")

                # Temperature notification settings
                temp_notifications_enabled = request.form.get(
                    "temp_notifications_enabled"
                )
                temp_threshold = request.form.get("temp_threshold")
                temp_cooldown = request.form.get("temp_cooldown")

                # Humidity notification settings
                humi_notifications_enabled = request.form.get(
                    "humi_notifications_enabled"
                )
                humi_threshold = request.form.get("humi_threshold")
                humi_cooldown = request.form.get("humi_cooldown")

                # Setting the received new settings
                self.db.set_user_settings(
                    advice_1,
                    advice_2,
                    advice_3,
                    advice_4,
                    advice_5,
                    advice_6,
                    fetch_sensor,
                    fetch_averages,
                    fetch_minmax,
                    notifications_enabled,
                    notification_threshold,
                    notification_cooldown,
                    notification_message,
                    email_notifications_enabled,
                    email_notification_threshold,
                    email_notification_cooldown,
                    email_address,
                    esp_alarm_enabled,
                    alarm_time,
                    temp_notifications_enabled,
                    temp_threshold,
                    temp_cooldown,
                    humi_notifications_enabled,
                    humi_threshold,
                    humi_cooldown,
                )

                return jsonify({"message": "Settings updated successfully!"}), 200
            except Exception as e:
                return {"message": f"Error updating settings: {str(e)}"}, 500

        @self.routes.route("/get_settings")
        def get_settings():
            """Returns all user settings from the db."""

            return self.db.get_user_settings()

        @self.routes.route("/default_settings", methods=["POST"])
        def set_default_settings():
            """Sets the default user settings."""

            try:
                # Setting the default settings
                self.db.set_default_settings()
                return ({"message": "Settings reset successfully!"}), 200
            except Exception as e:
                return {"message": f"Error resetting settings: {str(e)}"}, 500

        @self.routes.route("/notification_history")
        def get_notifications():
            """Returns all notifications from the db."""

            all_notifications = self.db.get_notification_history()

            # Converting notifications from the db into a json format
            all_notifications_json = [
                {"id": row[0], "timestamp": row[1], "message": row[2], "voc": row[3]}
                for row in all_notifications
            ]

            return jsonify(all_notifications_json)

        @self.routes.route("/notification_clear", methods=["POST"])
        def clear_notifications():
            """Clears all notifications."""

            try:
                # Clearing table with the notifications
                self.db.clear_table("notifications")
                return jsonify({"message": "Notifications successfully cleared!"}), 200
            except Exception as e:
                return (
                    jsonify({"message": f"Error clearing notifications: {str(e)}"}),
                    500,
                )

        @self.routes.route("/delete_notification", methods=["POST"])
        def delete_notification():
            """Deletes a selected notification using the id."""
            notification_id = request.json.get("id")
            print("Notification id: ", notification_id)
            try:
                self.db.delete_notification(notification_id)
                return jsonify({"message": "Notification successfully deleted!"}), 200
            except Exception as e:
                return (
                    jsonify({"message": f"Error deleting notifications: {str(e)}"}),
                    500,
                )

        @self.routes.route("/devices_list")
        def get_devices():
            """Returns a json list of all the devices in the db."""

            all_devices = self.db.get_all_devices()

            # Converting received list of devices from the db into a json format
            all_devices_json = [
                {"id": row[0], "device_name": row[1], "topic": row[2]}
                for row in all_devices
            ]

            return jsonify(all_devices_json)

        @self.routes.route("/new_device", methods=["POST"])
        def new_device():
            """Adds a new device to the db."""

            try:
                device_name = request.form.get("device_name")
                topic = request.form.get("topic")

                # Adding a new device and subscribing to the new topic in mqtt_manager
                self.db.new_device(device_name, topic)
                self.mqtt.subscribe(topic, device_name)

                return jsonify({"message": "New device added!"}), 200
            except Exception as e:
                return {"message": f"Error adding device: {str(e)}"}, 500

        @self.routes.route("/devices_clear", methods=["POST"])
        def clear_devices():
            """Clears all devices from the db."""

            try:
                # Clearing the table with all the devices and clearing topics in mqtt_manager
                self.db.clear_table("devices")
                self.mqtt.clear_topics()
                return jsonify({"message": "Notifications successfully cleared!"}), 200
            except Exception as e:
                return (
                    jsonify({"message": f"Error clearing notifications: {str(e)}"}),
                    500,
                )

        @self.routes.route("/delete_device", methods=["POST"])
        def delete_device():
            """Deletes the specified device from the db."""

            device_id = request.json.get("id")
            device_name = request.json.get("device_name")
            topic = request.json.get("topic")
            print("Device id: ", device_id)
            try:
                # Deleting a device based on it's name and id
                self.db.delete_device(device_id, device_name)
                # Unsubscribing from the topic of the deleted device
                self.mqtt.unsubscribe(topic)
                return jsonify({"message": "Device successfully deleted!"}), 200
            except Exception as e:
                return (
                    jsonify({"message": f"Error deleting device: {str(e)}"}),
                    500,
                )

        @self.routes.route("/select_device", methods=["POST"])
        def select_device():
            """Selects a device."""

            device_id = request.json.get("id")
            topic = request.json.get("topic")
            device_name = request.json.get("device_name")
            print("Select device params: ", device_id, topic, device_name)
            # Setting the selected device to the device user has clicked on
            self.selected_device = device_name
            return jsonify({"message": "New device selected!"}), 200

        @self.routes.route("/current_device")
        def get_current_device():
            return jsonify({"selected_device": self.selected_device})

        return self.routes

    def register_socket_events(self):
        """Registers used socket events."""

        @self.socketio.on("connect")
        def test_connect():
            """Tests the socket connection."""

            # If a socket connection isn't established yet, we establish it and notify the user
            if self.socket_connection_established is not True:
                print("Client connected!")
                self.socketio.emit(
                    "alert", {"message": "Welcome! Server is connected."}
                )
                self.socket_connection_established = True

    def check_sensor_data(
        self,
        notifications_on,
        email_notifications_on,
        voc,
        set_threshold,
        cooldown,
        notification_message,
        email_cooldown,
        email_notification_threshold,
        esp_alarm_enabled,
        alarm_time,
        temp_notifications_enabled,
        temp_threshold,
        temp_cooldown,
        humi_notifications_enabled,
        humi_threshold,
        humi_cooldown,
        humidity,
        temperature,
    ):
        """
        Checking passed parameter and handling the notifications

        Getting the current time, defining a timestamp, checking the parameters one by one and handling
        the notification logic.
        """

        current_time = time.time()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # If the voc is higher than user set threshold and the notifications are turned on
        if voc > set_threshold and notifications_on:
            if (
                not self.notification_sent
                or (current_time - self.last_notification) > cooldown
            ):
                # Sending a socket message with the user set notification message
                self.socketio.emit("alert", {"message": notification_message})

                # If an esp alarm is enabled we send a message using mqtt turning the alarm on
                if esp_alarm_enabled:
                    self.mqtt.threshold_exceeded_notification("on")

                # Adding the notification to our table of notification in the db
                self.db.new_notification(timestamp, notification_message, voc)

                # Setting the notification sent to True and last_notification to the current_time
                self.notification_sent = True
                self.last_notification = current_time

            # If the user set alarm notification time passed, turn off the alarm
            if (
                current_time - self.last_notification
            ) > alarm_time and esp_alarm_enabled:
                self.mqtt.threshold_exceeded_notification("off")
        else:
            self.notification_sent = False

        # If voc exceeded the threshold for an email notification and email notifications are on
        if voc > email_notification_threshold and email_notifications_on:
            if (
                not self.email_notification_sent
                or (current_time - self.last_email_notification) > email_cooldown
            ):
                # Sending an email with the message
                self.send_email_voc_threshold_exceeded(
                    timestamp, voc, notification_message
                )

                # Adding the notification to the db with the email-- prefix
                self.db.new_notification(
                    "email--" + timestamp, notification_message, voc
                )

                self.email_notification_sent = True
                self.last_email_notification = current_time
        else:
            self.email_notification_sent = False

        # If temperature has exceeded the user set limit and the temperature notification are on
        if temperature > temp_threshold and temp_notifications_enabled:
            if (
                not self.temp_notification_sent
                or (current_time - self.last_temp_notification) > temp_cooldown
            ):
                # Sending a socket message with the specified message
                self.socketio.emit(
                    "alert", {"message": "Temperature exceeded set value."}
                )

                self.temp_notification_sent = True
                self.last_temp_notification = current_time
        else:
            self.temp_notification_sent = False

        # If humidity has exceeded the user set limit and humidity notifications are on
        if humidity > humi_threshold and humi_notifications_enabled:
            if (
                not self.humi_notification_sent
                or (current_time - self.last_humi_notification) > humi_cooldown
            ):
                # Sending a socket message with the specified message
                self.socketio.emit("alert", {"message": "Humidity exceeded set value."})

                self.humi_notification_sent = True
                self.last_humi_notification = current_time
        else:
            self.humi_notification_sent = False

    def send_email(self, receiver, subject, body):
        """Sends an email with the specified parameters."""
        try:
            with current_app.app_context():
                message = Message(subject, recipients=receiver, body=body)
                self.mail.send(message)
                print("Email sent!")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def send_email_voc_threshold_exceeded(self, timestamp, voc_level, message):
        """Sends a specific email about exceeded voc threshold to a user set email address."""

        receiver_address = self.db.get_user_email_address()
        subject = "VOC Warning"
        body = f"{timestamp} \n Current VOC level: {voc_level}, set threshold exceeded. \n {message}"
        self.send_email(receiver_address, subject, body)
