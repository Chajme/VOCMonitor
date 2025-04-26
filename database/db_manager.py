"""Module handles database querries and connection."""

import os
import re
import sqlite3


class DatabaseManager:
    """Class represents a database manager."""

    def __init__(self):
        """Defined the db_name and attributes like connection and cursor."""

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.db_name = os.path.join(base_dir, "database", "database.db")

        self.selected_device = None

        self.initialize_db()

    def set_selected_device(self, new_device):
        self.selected_device = new_device

    def get_selected_device(self):
        return self.selected_device

    def initialize_db(self):
        """Initialize the db connection, cursor, create tables and set default user settings."""

        # self.clear_table("esp")
        # self.clear_table("device")

        # Create tables
        self.create_table_notification_history()
        self.create_user_settings_table()
        self.create_table_devices()

        # Setting default user settings
        self.set_default_settings()

    def _connect(self):
        """Connects to the db and returns the connection."""

        return sqlite3.connect(self.db_name)

    def insert(self, table_name, timestamp, temperature, humidity, voc):
        """Insert data into the specified data table."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                f"INSERT INTO {table_name} (timestamp, temperature, humidity, voc) VALUES (?, ?, ?, ?)",
                (timestamp, temperature, humidity, voc),
            )
            con.commit()

    def clear_table(self, table_name):
        """Clear the specified table."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(f"DELETE FROM {table_name}")
            con.commit()

    def delete_table(self, table_name):
        with self._connect() as con:
            cur = con.cursor()
            cur.execute(f"DROP TABLE IF EXISTS {table_name}")

    def create_table_data(self, table_name):
        """Create a table with the specified table_name."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} (timestamp, temperature, humidity, voc)"
            )
            con.commit()

    def create_table_devices(self):
        """Create table devices."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS devices ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, device_name TEXT UNIQUE, topic TEXT"
                ")"
            )
            con.commit()

    def new_device(self, device_name, topic):
        """Add a new device to the devices table."""

        with self._connect() as con:
            cur = con.cursor()

            if self.is_valid_device_name(device_name):
                cur.execute(
                    "INSERT OR IGNORE INTO devices (device_name, topic) VALUES (?, ?)",
                    (device_name, topic),
                )

                cur.execute(
                    f"CREATE TABLE IF NOT EXISTS {device_name} (timestamp, temperature, humidity, voc)"
                )
                con.commit()

    def delete_device(self, device_id, device_name):
        """Remove a device from the devices table."""

        with self._connect() as con:
            cur = con.cursor()

            cur.execute("SELECT id FROM devices WHERE id = ?", (device_id,))
            if not cur.fetchone():
                raise ValueError(f"Device ID {device_id} not found in the database")

            cur.execute("DELETE FROM devices WHERE id = ?", (device_id,))

            # Dropping the table with the devices data
            try:
                cur.execute(f"DROP TABLE IF EXISTS {device_name}")
            except Exception as e:
                print(f"Error dropping table: {e}")

            con.commit()

    def get_all_devices(self):
        """Return all the devices in the devices table."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id, device_name, topic FROM devices")
            con.commit()
            all_rows = cur.fetchall()
            return all_rows

    def get_device_topics(self):
        """Get all the device topics in the devices table."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT topic, device_name FROM devices")
            all_rows = cur.fetchall()
            return all_rows

    def create_table_notification_history(self):
        """Create a table to story all the notifications."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, message TEXT, voc INTEGER)"
            )
            con.commit()

    def new_notification(self, timestamp, message, voc):
        """Add a new notification to the notifications table."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO notifications (timestamp, message, voc) VALUES (?, ?, ?)",
                (timestamp, message, voc),
            )
            con.commit()

    def delete_notification(self, notification_id):
        """Remove a notification from the notifications table."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
            con.commit()

    def get_notification_history(self):
        """Get all the notifications in the notifications table."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT id, timestamp, message, voc FROM notifications ORDER BY timestamp DESC"
            )
            con.commit()
            all_rows = cur.fetchall()
            return all_rows

    def create_user_settings_table(self):
        """Create a table to store user settings."""

        print("Creating user settings table...")

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS user_settings ("
                "id INTEGER PRIMARY KEY,"
                "advice1 TEXT,"
                "advice2 TEXT,"
                "advice3 TEXT,"
                "advice4 TEXT,"
                "advice5 TEXT,"
                "advice6 TEXT,"
                "fetchSensor INTEGER,"
                "fetchAverages INTEGER,"
                "fetchMinmax INTEGER,"
                "notifications INTEGER DEFAULT 1,"
                "notification_threshold INTEGER,"
                "cooldown INTEGER,"
                "notification_message TEXT,"
                "email_notifications_on INTEGER DEFAULT 1,"
                "email_notification_threshold INTEGER,"
                "email_cooldown INTEGER,"
                "email_address TEXT,"
                "esp_alarm_enabled INTEGER DEFAULT 1,"
                "alarm_time INTEGER,"
                "temp_notifications_enabled INTEGER DEFAULT 0,"
                "temp_threshold INTEGER,"
                "temp_cooldown INTEGER,"
                "humi_notifications_enabled INTEGER DEFAULT 0,"
                "humi_threshold INTEGER,"
                "humi_cooldown INTEGER)"
            )
            con.commit()

    def set_user_settings(
        self,
        advice_1,
        advice_2,
        advice_3,
        advice_4,
        advice_5,
        advice_6,
        fetch_sensor,
        fetch_averages,
        fetch_minmax,
        notifications,
        notification_threshold,
        cooldown,
        notification_message,
        email_notifications_on,
        email_notification_threshold,
        email_cooldown,
        email_address,
        esp_alarm_enabled,
        alarm_time,
        temp_notifications_enabled,
        temp_threshold,
        temp_cooldown,
        humi_notifications_enabled,
        humi_threshold,
        humi_cooldown,
    ):
        """Set user settings in the user settings table."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                    INSERT INTO user_settings (
                    id,
                    advice1,
                    advice2,
                    advice3,
                    advice4,
                    advice5,
                    advice6,
                    fetchSensor, 
                    fetchAverages, 
                    fetchMinmax, 
                    notifications, 
                    notification_threshold,
                    cooldown,
                    notification_message,
                    email_notifications_on, 
                    email_notification_threshold,
                    email_cooldown,
                    email_address,
                    esp_alarm_enabled,
                    alarm_time,
                    temp_notifications_enabled,
                    temp_threshold,
                    temp_cooldown,
                    humi_notifications_enabled,
                    humi_threshold,
                    humi_cooldown 
                    ) 
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        advice1 = excluded.advice1,
                        advice2 = excluded.advice2,
                        advice3 = excluded.advice3,
                        advice4 = excluded.advice4,
                        advice5 = excluded.advice5,
                        advice6 = excluded.advice6,
                        fetchSensor = excluded.fetchSensor,
                        fetchAverages = excluded.fetchAverages,
                        fetchMinmax = excluded.fetchMinmax,
                        notifications = excluded.notifications,
                        notification_threshold = excluded.notification_threshold,
                        cooldown = excluded.cooldown,
                        notification_message = excluded.notification_message,
                        email_notifications_on = excluded.email_notifications_on,
                        email_notification_threshold = excluded.email_notification_threshold,
                        email_cooldown = excluded.email_cooldown,
                        email_address = excluded.email_address,
                        esp_alarm_enabled = excluded.esp_alarm_enabled,
                        alarm_time = excluded.alarm_time,
                        temp_notifications_enabled = excluded.temp_notifications_enabled,
                        temp_threshold = excluded.temp_threshold,
                        temp_cooldown = excluded.temp_cooldown,
                        humi_notifications_enabled = excluded.humi_notifications_enabled,
                        humi_threshold = excluded.humi_threshold,
                        humi_cooldown = excluded.humi_cooldown
                    """,
                (
                    advice_1,
                    advice_2,
                    advice_3,
                    advice_4,
                    advice_5,
                    advice_6,
                    fetch_sensor,
                    fetch_averages,
                    fetch_minmax,
                    notifications,
                    notification_threshold,
                    cooldown,
                    notification_message,
                    email_notifications_on,
                    email_notification_threshold,
                    email_cooldown,
                    email_address,
                    esp_alarm_enabled,
                    alarm_time,
                    temp_notifications_enabled,
                    temp_threshold,
                    temp_cooldown,
                    humi_notifications_enabled,
                    humi_threshold,
                    humi_cooldown,
                ),
            )
            con.commit()

    def get_user_settings(self):
        """Get all the use settings from the user settings table."""
        
        with self._connect() as con:
            cur = con.cursor()
            query = """
                SELECT advice1, advice2, advice3, advice4, advice5, advice6,
                       fetchSensor, fetchAverages, fetchMinmax, notifications,
                       notification_threshold, cooldown, notification_message,
                       email_notifications_on, email_notification_threshold, email_cooldown, email_address, esp_alarm_enabled,
                       alarm_time, temp_notifications_enabled, temp_threshold, temp_cooldown, humi_notifications_enabled,
                       humi_threshold, humi_cooldown 
                FROM user_settings WHERE id=1
            """
            result = cur.execute(query).fetchone()
            if result:
                return {
                    "advice1": result[0],
                    "advice2": result[1],
                    "advice3": result[2],
                    "advice4": result[3],
                    "advice5": result[4],
                    "advice6": result[5],
                    "fetch_sensor": result[6],
                    "fetch_averages": result[7],
                    "fetch_minmax": result[8],
                    "notifications": bool(result[9]),
                    "notification_threshold": result[10],
                    "cooldown": result[11],
                    "notification_message": result[12],
                    "email_notifications_on": bool(result[13]),
                    "email_notification_threshold": result[14],
                    "email_cooldown": result[15],
                    "email_address": result[16],
                    "esp_alarm_enabled": bool(result[17]),
                    "alarm_time": result[18],
                    "temp_notifications_enabled": bool(result[19]),
                    "temp_threshold": result[20],
                    "temp_cooldown": result[21],
                    "humi_notifications_enabled": bool(result[22]),
                    "humi_threshold": result[23],
                    "humi_cooldown": result[24],
                }
            else:
                return {
                    "advice1": "",
                    "advice2": "",
                    "advice3": "",
                    "advice4": "",
                    "advice5": "",
                    "advice6": "",
                    "fetch_sensor": 0,
                    "fetch_averages": 0,
                    "fetch_minmax": 0,
                    "notifications": False,
                    "notification_threshold": 0,
                    "cooldown": 0,
                    "notification_message": "",
                    "email_notifications_on": False,
                    "email_notification_threshold": 0,
                    "email_cooldown": 0,
                    "email_address": "",
                    "esp_alarm_enabled": 0,
                    "alarm_time": 0,
                    "temp_notifications_enabled": False,
                    "temp_threshold": 0,
                    "temp_cooldown": 0,
                    "humi_notifications_enabled": False,
                    "humi_threshold": 0,
                    "humi_cooldown": 0,
                }

    def get_user_settings_notifications(self):
        """Get user settings, specifically the setting about the notifications."""

        with self._connect() as con:
            cur = con.cursor()
            query = (
                "SELECT notifications, "
                "notification_threshold, "
                "cooldown, "
                "notification_message, "
                "email_notifications_on, "
                "email_notification_threshold, "
                "email_cooldown, "
                "esp_alarm_enabled, "
                "alarm_time,"
                "temp_notifications_enabled,"
                "temp_threshold,"
                "temp_cooldown,"
                "humi_notifications_enabled,"
                "humi_threshold,"
                "humi_cooldown "
                "FROM user_settings WHERE id=1"
            )
            result = cur.execute(query).fetchone()
            (
                notifications_on,
                notification_threshold,
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
            ) = result

            return (
                notifications_on,
                notification_threshold,
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
            )

    def get_user_email_address(self):
        """Getting the user set email address."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT email_address from user_settings where id=1")
            email_address = cur.fetchone()
            return email_address

    def set_default_settings(self):
        """Setting the default user settings."""

        self.set_user_settings(
            "No action needed.",
            "Current VOC levels are good, no action is necessary.",
            "VOC levels are higher, you should open a window.",
            "Poor air quality, open a window.",
            "Very bad air quality, open a window immediately.",
            "Hazardous air quality, open a window and vacate the room immediately.",
            5000,
            30000,
            45000,
            1,
            200,
            300,
            "Poor air quality, open a window.",
            1,
            300,
            7200,
            "erikmolitoris60@gmail.com",
            1,
            5,
            0,
            0,
            300,
            0,
            50,
            300,
        )

    def print_table(self, table_name):
        """Printing a table with the specified table name."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM {table_name}")
            print(cur.fetchall())

    def drop_table(self, table_name):
        """Dropping a table with the specified table name."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(f"DROP TABLE IF EXISTS {table_name}")
            con.commit()

    def get_last_row(self, table_name):
        """Returning the last row from the specified table."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            result = cur.fetchone()
            num_of_rows = result[0]

            """query = "SELECT * FROM {} ORDER BY timestamp DESC LIMIT 1".format(table_name)
            cur.execute(query)
            last_row = cur.fetchone()"""

            if num_of_rows > 0:
                last_row = cur.execute(f"SELECT * FROM {table_name}").fetchall()[-1]
                return last_row
            return None

    def get_all_rows(self, table_name):
        """Returning all the rows from the specified table."""

        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                f"SELECT timestamp, temperature, humidity, voc FROM {table_name} ORDER BY timestamp "
            )
            all_rows = cur.fetchall()

            return all_rows

    def get_all_data_from_timestamp(self, table_name, from_timestamp):
        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                f"SELECT * FROM {table_name} WHERE timestamp >= ?", (from_timestamp,)
            )
            rows = cur.fetchall()
            return rows

    def get_avg(self, time_period, table_name):
        """Return the average for the data from the specified table withing the specified time range."""

        with self._connect() as con:
            cur = con.cursor()

            query = f"SELECT AVG(voc) AS avg_voc FROM {table_name} WHERE timestamp >= datetime('now', ?)"
            cur.execute(query, (time_period,))

            avg_voc = cur.fetchone()[0]
            avg_voc = round(avg_voc, 2)
            return avg_voc

    def get_min_max(self, time_period, table_name):
        """Get the minimum and maximum from the specified table within the specified timerange."""

        with self._connect() as con:
            cur = con.cursor()

            query = f"SELECT MIN(voc), MAX(voc) FROM {table_name} WHERE timestamp >= datetime('now', ?)"
            cur.execute(query, (time_period,))

            min_max_voc = cur.fetchone()
            min_voc, max_voc = min_max_voc

            return min_voc, max_voc

    @staticmethod
    def is_valid_device_name(device_name):
        """Check if the specified device name is valid and return true or false."""

        pattern = r"^[a-z_][a-z0-9_]*$"
        return bool(re.match(pattern, device_name))
