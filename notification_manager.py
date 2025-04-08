import datetime
import time

from flask import current_app
from flask_mail import Message


class NotificationManager:
    def __init__(self, socketio, mail, db):
        self.last_notification = 0
        self.notification_sent = False
        self.last_email_notification = 0
        self.email_notification_sent = False
        self.last_temp_notification = 0
        self.temp_notification_sent = False
        self.last_humi_notification = 0
        self.humi_notification_sent = False

        self.notifications_on = None
        self.email_notifications_on = None

        self.esp_alarm_enabled = None
        self.send_esp_alarm = False

        self.temp_notifications_enabled = None
        self.humi_notifications_enabled = None

        self.email_cooldown = None
        self.email_notification_threshold = None
        self.notification_message = None

        self.selected_device = None

        self.socketio = socketio
        self.mail = mail
        self.db = db

    def set_notification_settings(
        self,
        notifications_on,
        email_notifications_on,
        esp_alarm_enabled,
        temp_notifications_enabled,
        humi_notifications_enabled,
        email_cooldown,
        email_notification_threshold,
        notification_message,
    ):
        self.notifications_on = notifications_on
        self.email_notifications_on = email_notifications_on
        self.esp_alarm_enabled = esp_alarm_enabled
        self.temp_notifications_enabled = temp_notifications_enabled
        self.humi_notifications_enabled = humi_notifications_enabled

        self.email_cooldown = email_cooldown
        self.email_notification_threshold = email_notification_threshold
        self.notification_message = notification_message

    def is_esp_alarm_enabled(self):
        return self.esp_alarm_enabled

    def check_for_notifications(
        self,
        voc,
        set_threshold,
        cooldown,
        notification_message,
        alarm_time,
        email_cooldown,
        email_notification_threshold,
        temp_threshold,
        temp_cooldown,
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
        if voc > set_threshold and self.notifications_on:
            if (
                not self.notification_sent
                or (current_time - self.last_notification) > cooldown
            ):
                # Sending a socket message with the user set notification message
                self.socketio.emit("alert", {"message": notification_message})

                # If an esp alarm is enabled we send a message using mqtt turning the alarm on
                if self.esp_alarm_enabled:
                    self.send_esp_alarm = True

                # Adding the notification to our table of notification in the db
                self.db.new_notification(timestamp, notification_message, voc)

                # Setting the notification sent to True and last_notification to the current_time
                self.notification_sent = True
                self.last_notification = current_time

            # If the user set alarm notification time passed, turn off the alarm
            if (
                current_time - self.last_notification
            ) > alarm_time and self.esp_alarm_enabled:
                self.send_esp_alarm = False
        else:
            self.notification_sent = False

        # If voc exceeded the threshold for an email notification and email notifications are on
        if voc > email_notification_threshold and self.email_notifications_on:
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
        if temperature > temp_threshold and self.temp_notifications_enabled:
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
        if humidity > humi_threshold and self.humi_notifications_enabled:
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

    def send_esp_alarm_notif(self, voc, device):
        return self.send_esp_alarm

    def check_email_notif(self, voc, device):
        current_time = time.time()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if (
            voc > self.email_notification_threshold
            and self.email_notifications_on
            and self.db.get_selected_device() == device
        ):
            if (
                not self.email_notification_sent
                or (current_time - self.last_email_notification) > self.email_cooldown
            ):
                # Sending an email with the message
                self.send_email_voc_threshold_exceeded(
                    timestamp, voc, self.notification_message
                )

                # Adding the notification to the db with the email-- prefix
                self.db.new_notification(
                    "email--" + timestamp, self.notification_message, voc
                )

                self.email_notification_sent = True
                self.last_email_notification = current_time
        else:
            self.email_notification_sent = False

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
