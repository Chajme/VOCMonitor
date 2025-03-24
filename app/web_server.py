import datetime
import time
from socket import SocketIO

from flask import Flask, jsonify, render_template, request
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit  # noqa: F811

from app.config import Config
from database.db_manager import DatabaseManager


class WebServer:
    def __init__(self, mqtt_manager):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)

        # Setting an app config for mail notifications
        self.set_app_config()
        self.mail = Mail(self.app)

        # Defining managers
        self.db = DatabaseManager()
        self.mqtt = mqtt_manager

        # Notification sent and cooldown tracking
        self.last_notification = 0
        self.notification_sent = False
        self.last_email_notification = 0
        self.email_notification_sent = False
        self.last_temp_notification = 0
        self.temp_notification_sent = False
        self.last_humi_notification = 0
        self.humi_notification_sent = False

        self.socket_connection_established = False

        self.db.new_device("esp", "data")
        self.db.new_device("device", "new/topic")

        self.selected_topic = "data"
        self.selected_device = "esp"

        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/compact")
        def compact():
            return render_template("compact.html")

        @self.app.route("/chart")
        def chart():
            return render_template("chart.html")

        @self.app.route("/devices")
        def devices():
            return render_template("devices.html")

        @self.app.route("/settings")
        def settings():
            return render_template("settings.html")

        @self.app.route("/all-data")
        def all_data():
            all_data_row = self.db.get_all_rows(self.selected_device)

            all_data_list = {
                "timestamp": [row[0] for row in all_data_row],
                "temperature": [row[1] for row in all_data_row],
                "humidity": [row[2] for row in all_data_row],
                "voc_index": [row[3] for row in all_data_row],
            }

            data_json = jsonify(all_data_list)
            return data_json

        @self.app.route("/data")
        def new_data():
            try:
                new_data_row = self.db.get_last_row(self.selected_device)
                print("/data new_data_row: ", new_data_row)

                if not new_data_row:
                    return jsonify({"message": "No data available"}), 404

                print(new_data_row)

                new_data_list = {
                    "timestamp": new_data_row[0],
                    "temperature": new_data_row[1],
                    "humidity": new_data_row[2],
                    "voc_index": new_data_row[3],
                }

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

                if (
                    notifications_on == 1
                    or email_notifications_on == 1
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

        @self.app.route("/avg")
        def get_averages():
            try:
                avg_24h = self.db.get_avg("-24 hours", self.selected_device)
                avg_72h = self.db.get_avg("-72 hours", self.selected_device)
                avg_7d = self.db.get_avg("-7 days", self.selected_device)

                averages = {"avg_24h": avg_24h, "avg_72h": avg_72h, "avg_7d": avg_7d}
            except Exception as e:
                return jsonify({"message": f"Error fetching averages {e}"}), 500

            return jsonify(averages), 200

        @self.app.route("/minmax")
        def get_min_max_voc():
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

        @self.app.route("/update_settings", methods=["POST"])
        def update_settings():
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

        @self.app.route("/get_settings")
        def get_settings():
            return self.db.get_user_settings()

        @self.app.route("/default_settings", methods=["POST"])
        def set_default_settings():
            try:
                self.db.set_default_settings()
                return ({"message": "Settings reset successfully!"}), 200
            except Exception as e:
                return {"message": f"Error resetting settings: {str(e)}"}, 500

        @self.app.route("/notification_history")
        def get_notifications():
            all_notifications = self.db.get_notification_history()

            """all_notifications_json = {
                "id": [row[0] for row in all_notifications],   
                "timestamp": [row[1] for row in all_notifications],
                "message": [row[2] for row in all_notifications],
                "voc": [row[3] for row in all_notifications],
            }"""

            all_notifications_json = [
                {"id": row[0], "timestamp": row[1], "message": row[2], "voc": row[3]}
                for row in all_notifications
            ]

            return jsonify(all_notifications_json)

        @self.app.route("/notification_clear", methods=["POST"])
        def clear_notifications():
            try:
                self.db.clear_table("notifications")
                return jsonify({"message": "Notifications successfully cleared!"}), 200
            except Exception as e:
                return (
                    jsonify({"message": f"Error clearing notifications: {str(e)}"}),
                    500,
                )

        @self.app.route("/delete_notification", methods=["POST"])
        def delete_notification():
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

        @self.app.route("/devices_list")
        def get_devices():
            all_devices = self.db.get_all_devices()

            all_devices_json = [
                {"id": row[0], "device_name": row[1], "topic": row[2]}
                for row in all_devices
            ]

            return jsonify(all_devices_json)

        @self.app.route("/new_device", methods=["POST"])
        def new_device():
            try:
                device_name = request.form.get("device_name")
                topic = request.form.get("topic")

                self.db.new_device(device_name, topic)

                return jsonify({"message": "New device added!"}), 200
            except Exception as e:
                return {"message": f"Error adding device: {str(e)}"}, 500

        @self.app.route("/devices_clear", methods=["POST"])
        def clear_devices():
            try:
                self.db.clear_table("devices")
                return jsonify({"message": "Notifications successfully cleared!"}), 200
            except Exception as e:
                return (
                    jsonify({"message": f"Error clearing notifications: {str(e)}"}),
                    500,
                )

        @self.app.route("/delete_device", methods=["POST"])
        def delete_device():
            device_id = request.json.get("id")
            device_name = request.json.get("device_name")
            topic = request.json.get("topic")
            print("Device id: ", device_id)
            try:
                self.db.delete_device(device_id, device_name)
                self.mqtt.unsubscribe(topic)
                return jsonify({"message": "Device successfully deleted!"}), 200
            except Exception as e:
                return (
                    jsonify({"message": f"Error deleting device: {str(e)}"}),
                    500,
                )

        @self.app.route("/select_device", methods=["POST"])
        def select_device():
            device_id = request.json.get("id")
            topic = request.json.get("topic")
            device_name = request.json.get("device_name")
            print("Select device params: ", device_id, topic, device_name)
            self.mqtt.subscribe(topic, device_name)
            self.selected_topic = topic
            self.selected_device = device_name
            return jsonify({"message": "New device selected!"}), 200

        @self.socketio.on("connect")
        def test_connect():
            if self.socket_connection_established is not True:
                print("Client connected!")
                emit("alert", {"message": "Welcome! Server is connected."})
                self.socket_connection_established = True

        self.app.run()

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
        current_time = time.time()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if voc > set_threshold and notifications_on == 1:
            if (
                not self.notification_sent
                or (current_time - self.last_notification) > cooldown
            ):
                self.socketio.emit("alert", {"message": notification_message})

                if esp_alarm_enabled == 1:
                    self.mqtt.threshold_exceeded_notification("on")

                self.db.new_notification(timestamp, notification_message, voc)

                self.notification_sent = True
                self.last_notification = current_time

                """self.send_email_voc_threshold_exceeded(timestamp, voc, message)"""
            if (
                current_time - self.last_notification
            ) > alarm_time and esp_alarm_enabled == 1:
                self.mqtt.threshold_exceeded_notification("off")
                print("Setting threshold exceeded to off")
        else:
            self.notification_sent = False

        if voc > email_notification_threshold and email_notifications_on == 1:
            if (
                not self.email_notification_sent
                or (current_time - self.last_email_notification) > email_cooldown
            ):
                self.send_email_voc_threshold_exceeded(
                    timestamp, voc, notification_message
                )

                self.db.new_notification(
                    "email--" + timestamp, notification_message, voc
                )

                self.email_notification_sent = True
                self.last_email_notification = current_time
        else:
            self.email_notification_sent = False

        if temperature > temp_threshold and temp_notifications_enabled == 1:
            if (
                not self.temp_notification_sent
                or (current_time - self.last_temp_notification) > temp_cooldown
            ):
                self.socketio.emit(
                    "alert", {"message": "Temperature exceeded set value."}
                )
                self.temp_notification_sent = True
                self.last_temp_notification = current_time
        else:
            self.temp_notification_sent = False

        if humidity > humi_threshold and humi_notifications_enabled == 1:
            if (
                not self.humi_notification_sent
                or (current_time - self.last_humi_notification) > humi_cooldown
            ):
                self.socketio.emit("alert", {"message": "Humidity exceeded set value."})
                self.humi_notification_sent = True
                self.last_humi_notification = current_time
        else:
            self.humi_notification_sent = False

    def set_app_config(self):
        self.app.config.from_object(Config)

    def send_email(self, receiver, subject, body):
        try:
            with self.app.app_context():
                message = Message(subject, recipients=[receiver], body=body)
                self.mail.send(message)
                print("Email sent!")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def send_email_voc_threshold_exceeded(self, timestamp, voc_level, message):
        receiver_address = self.db.get_user_email_address()
        subject = "VOC Warning"
        body = f"{timestamp} \n Current VOC level: {voc_level}, set threshold exceeded. \n {message}"
        self.send_email(receiver_address, subject, body)
