import datetime
import time

import paho.mqtt.client as mqtt

from database.db_manager import DatabaseManager


class MQTTManager:
    def __init__(self):
        self.server = "192.168.0.103"
        self.port = 1883
        self.topic = "data"
        self.table_name = "esp"
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="pc", protocol=mqtt.MQTTv5
        )  # protocol=mqtt.CallbackAPIVersion.VERSION2

        self.db_manager = DatabaseManager()
        self.voc_index_array = []

        self.threshold_exceeded = False

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("MQTT connection established")
            client.subscribe(self.topic)
        else:
            print(f"Connection error: {str(reason_code)}")

    def on_message(self, client, userdata, message):
        msg_str = str(message.payload.decode())
        msg_split = msg_str.split(",")
        temperature = msg_split[0]
        humidity = msg_split[1]
        voc = msg_split[2]

        self.voc_index_array.append(int(voc))

        curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if len(self.voc_index_array) == 5:
            # avg_voc = int(sum(self.voc_index_array) / len(self.voc_index_array)) #For testing we only store every 5th value
            self.db_manager.insert(
                self.table_name, curr_time, temperature, humidity, voc
            )
            self.voc_index_array.clear()

        # curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # self.db_manager.insert(curr_time, temp, humi, voc)
        print(self.db_manager.get_last_row(self.table_name))

    def run_mqtt(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        result = None

        while result is None or result != 0:
            try:
                result = self.client.connect(self.server, self.port, 60)
            except Exception as e:
                print(f"Connection failed: {e}")
                print("Will try reconnecting in 15 seconds...")
            time.sleep(15)

        self.client.subscribe(self.topic)

        try:
            """self.client.loop_forever()"""
            self.client.loop_start()
        except KeyboardInterrupt:
            self.client.disconnect()

    def subscribe(self, topic, device_name):
        self.set_topic(topic)
        self.client.subscribe(self.topic)
        self.set_table_name(device_name)
        print("Subscribed to new topic: ", self.topic)

    def unsubscribe(self):
        self.client.unsubscribe(self.topic)
        print("Unsubscribed from topic: ", self.topic)

    def set_topic(self, topic):
        self.topic = topic

    def set_table_name(self, table_name):
        self.table_name = table_name

    def threshold_exceeded_notification(self, payload):
        self.client.publish("alert/testing", payload)
        print("LED state changed: ", payload)
