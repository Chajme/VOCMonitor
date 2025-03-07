import time
from socket import SocketIO

import datetime
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

from database.db_manager import DatabaseManager
from flask_mail import Mail, Message


class WebServer:

    def __init__(self, mqtt_manager):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)

        self.set_mail_config()
        self.mail = Mail(self.app)

        self.db = DatabaseManager()
        self.mqtt = mqtt_manager

        self.last_notification = 0
        self.notification_sent = False
        self.last_email_notification = 0
        self.email_notification_sent = False

        self.socket_connection_established = False

        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/compact")
        def compact():
            return render_template("compact.html")

        @self.app.route("/chart")
        def chart():
            return render_template("chart.html")

        @self.app.route("/settings")
        def settings():
            return render_template("settings.html")

        @self.app.route("/all-data")
        def all_data():
            all_data_row = self.db.get_all_rows()

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
                new_data_row = self.db.get_last_row()

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
                ) = self.db.get_user_settings_notifications()

                if (
                    notifications_on == 1
                    or email_notifications_on == 1
                    and self.db.get_last_row() is not None
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
                    )
                    return jsonify(new_data_list), 200

            except Exception as e:
                return jsonify({"message": f"Error fetching new data: {str(e)}"}), 500

        @self.app.route("/avg")
        def get_averages():
            try:
                avg_24h = self.db.get_avg("-24 hours")
                avg_72h = self.db.get_avg("-72 hours")
                avg_7d = self.db.get_avg("-7 days")

                averages = {"avg_24h": avg_24h, "avg_72h": avg_72h, "avg_7d": avg_7d}
            except Exception as e:
                return jsonify({"message": f"Error fetching averages {e}"}), 500

            return jsonify(averages), 200

        @self.app.route("/minmax")
        def get_min_max_voc():
            try:
                min_24h, max_24h = self.db.get_min_max("-24 hours")
                min_72h, max_72h = self.db.get_min_max("-72 hours")

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
                advice_1 = request.form.get("advice_1")
                advice_2 = request.form.get("advice_2")
                advice_3 = request.form.get("advice_3")
                advice_4 = request.form.get("advice_4")
                advice_5 = request.form.get("advice_5")
                advice_6 = request.form.get("advice_6")

                fetch_sensor = request.form.get("fetch_sensor")
                fetch_averages = request.form.get("fetch_averages")
                fetch_minmax = request.form.get("fetch_minmax")

                notifications_enabled = (
                    request.form.get("notifications_enabled") == "true"
                )
                notification_threshold = request.form.get("notification_threshold")
                notification_cooldown = request.form.get("notification_cooldown")
                notification_message = request.form.get("notification_message")

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

                esp_alarm_enabled = request.form.get("esp_alarm_enabled")
                alarm_time = request.form.get("alarm_time")

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
            print(all_notifications)

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

    def set_mail_config(self):
        self.app.config["MAIL_SERVER"] = "smtp.gmail.com"
        self.app.config["MAIL_PORT"] = 465
        self.app.config["MAIL_USE_TLS"] = False
        self.app.config["MAIL_USE_SSL"] = True
        self.app.config["MAIL_USERNAME"] = "vocmonitorsystem@gmail.com"
        self.app.config["MAIL_PASSWORD"] = "krrr hqwg bdfw vgfo"
        self.app.config["MAIL_DEFAULT_SENDER"] = "vocmonitorsystem@gmail.com"

    def send_email(self, receiver, subject, body):
        try:
            with self.app.app_context():
                message = Message(subject, recipients=[receiver], body=body)
                self.mail.send(message)
                print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def send_email_voc_threshold_exceeded(self, timestamp, voc_level, message):
        receiver_address = self.db.get_user_email_address()
        subject = "VOC Warning"
        body = f"{timestamp} \n Current VOC level: {voc_level}, set threshold exceeded. \n {message}"
        self.send_email(receiver_address, subject, body)
