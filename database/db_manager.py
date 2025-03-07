import sqlite3


class DatabaseManager:

    def __init__(self):
        self.db_name = "database/database.db"

        self.con = None
        self.cur = None

        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()

        # Clearing the db and dropping tables
        self.clear_table("data")
        self.drop_table("user_settings")
        # self.drop_table("notifications")

        # Create tables
        self.create_table_data()
        self.create_table_notification_history()
        self.create_user_settings_table()

        # Setting default user settings
        self.set_default_settings()

        self.con.close()

    def insert(self, timestamp, temperature, humidity, voc):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute(
            "INSERT INTO data (timestamp, temperature, humidity, voc) VALUES (?, ?, ?, ?)",
            (timestamp, temperature, humidity, voc),
        )
        self.con.commit()
        self.con.close()

    def clear_table(self, table_name):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute(f"DELETE FROM {table_name}")
        # self.cur.execute("DELETE FROM user_settings")
        self.con.commit()
        self.con.close()

    def create_table_data(self):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS data (timestamp, temperature, humidity, voc)"
        )
        self.con.commit()
        self.con.close()

    def create_table_notification_history(self):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, message TEXT, voc INTEGER)"
        )
        self.con.commit()
        self.con.close()

    def new_notification(self, timestamp, message, voc):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute(
            "INSERT INTO notifications (timestamp, message, voc) VALUES (?, ?, ?)",
            (timestamp, message, voc),
        )
        self.con.commit()
        self.con.close()

    def delete_notification(self, notification_id):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
        self.con.commit()
        self.con.close()

    def get_notification_history(self):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute(
            "SELECT id, timestamp, message, voc FROM notifications ORDER BY timestamp DESC"
        )
        self.con.commit()
        all_rows = self.cur.fetchall()
        self.con.close()
        return all_rows

    def create_user_settings_table(self):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute(
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
            "alarm_time INTEGER)"
        )
        self.con.commit()
        self.con.close()

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
    ):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute(
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
                alarm_time  
) 
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    alarm_time = excluded.alarm_time
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
            ),
        )
        self.con.commit()
        self.con.close()

    def get_user_settings(self):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        query = """
            SELECT advice1, advice2, advice3, advice4, advice5, advice6,
                   fetchSensor, fetchAverages, fetchMinmax, notifications,
                   notification_threshold, cooldown, notification_message,
                   email_notifications_on, email_notification_threshold, email_cooldown, email_address, esp_alarm_enabled,
                   alarm_time 
            FROM user_settings WHERE id=1
        """
        result = self.cur.execute(query).fetchone()
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
                "esp_alarm_enabled": result[17],
                "alarm_time": result[18],
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
            }

    def get_user_settings_notifications(self):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        query = (
            "SELECT notifications, "
            "notification_threshold, "
            "cooldown, "
            "notification_message, "
            "email_notifications_on, "
            "email_notification_threshold, "
            "email_cooldown, "
            "esp_alarm_enabled, "
            "alarm_time "
            "FROM user_settings WHERE id=1"
        )
        result = self.cur.execute(query).fetchone()
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
        )

    def get_user_email_address(self):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute("SELECT email_address from user_settings where id=1")
        email_address = self.cur.fetchone()
        return email_address

    def set_default_settings(self):
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
            10,
        )

    def print_table(self, table_name):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute(f"SELECT * FROM {table_name}")
        print(self.cur.fetchall())
        self.con.close()

    def drop_table(self, table_name):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.con.commit()
        self.con.close()

    def get_last_row(self):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()

        self.cur.execute("SELECT COUNT(*) FROM data")
        result = self.cur.fetchone()
        num_of_rows = result[0]

        if num_of_rows > 0:
            last_row = self.cur.execute("SELECT * FROM data").fetchall()[-1]
            return last_row

        self.con.close()
        return None

    def get_all_rows(self):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute(
            "SELECT timestamp, temperature, humidity, voc FROM data ORDER BY timestamp "
        )
        all_rows = self.cur.fetchall()
        self.con.close()
        return all_rows

    def print_database(self):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        self.cur.execute("SELECT * FROM data")
        print(self.cur.fetchall())
        self.con.close()

    def get_avg(self, time_period):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()

        query = (
            "SELECT AVG(voc) AS avg_voc FROM data WHERE timestamp >= datetime('now', ?)"
        )
        self.cur.execute(query, (time_period,))

        avg_voc = self.cur.fetchone()[0]
        avg_voc = round(avg_voc, 2)
        self.con.close()
        return avg_voc

    def get_min_max(self, time_period):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()

        query = (
            "SELECT MIN(voc), MAX(voc) FROM data WHERE timestamp >= datetime('now', ?)"
        )
        self.cur.execute(query, (time_period,))

        min_max_voc = self.cur.fetchone()
        min_voc, max_voc = min_max_voc

        self.con.close()
        return min_voc, max_voc
