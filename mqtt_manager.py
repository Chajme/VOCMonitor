import datetime
import time

import paho.mqtt.client as mqtt


class MQTTManager:
    def __init__(self, db):
        self.server = "192.168.0.103"
        self.port = 1883
        self.selected_device = "esp"
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="pc", protocol=mqtt.MQTTv5
        )

        self.db_manager = db

        self.topics = {}
        self.voc_index = {}

        self.threshold_exceeded = False

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("MQTT connection to the broker established!")
            """client.subscribe(self.topic)"""

            self.load_topics_from_db()
            self.print_loaded_topics()
            self.subscribe_to_all_topics()
        else:
            print(f"Connection error: {str(reason_code)}")

    def on_message(self, client, userdata, message):
        msg_str = str(message.payload.decode())
        msg_split = msg_str.split(",")

        if len(msg_split) < 3:
            print(f"Invalid message received: {msg_str}")
            return

        temperature, humidity, voc = msg_split[0], msg_split[1], msg_split[2]

        if message.topic in self.topics:
            table_name = self.topics[message.topic]

            self.voc_index[table_name].append(int(voc))
            curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if len(self.voc_index[table_name]) == 5:
                avg_voc = int(
                    sum(self.voc_index[table_name]) / len(self.voc_index[table_name])
                )
                self.db_manager.insert(
                    table_name, curr_time, temperature, humidity, avg_voc
                )
                self.voc_index[table_name].clear()
                print(f"{table_name}: {self.db_manager.get_last_row(table_name)}")

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

        """self.client.subscribe(self.topic)
        self.client.subscribe("new/topic")"""

        try:
            self.client.loop_start()
        except KeyboardInterrupt:
            self.client.disconnect()

    def subscribe(self, topic, device_name):
        if topic not in self.topics:
            self.topics[topic] = device_name
            self.voc_index[device_name] = []
            self.client.subscribe(topic)
        print(f"Subscribed to new topic: {topic}, Table: {device_name}")

    def unsubscribe(self, topic):
        if topic in self.topics:
            table_name = self.topics[topic]
            self.client.unsubscribe(topic)

            del self.topics[topic]
            del self.voc_index[table_name]
            print(f"Unsubscribed from topic: {topic}, Removed table: {table_name}")

    def load_topics_from_db(self):
        rows = self.db_manager.get_device_topics()
        for topic, device_name in rows:
            self.topics[topic] = device_name
            self.voc_index[device_name] = []
        print("Loaded topics: ", self.topics)

    def subscribe_to_all_topics(self):
        for topic in self.topics.keys():
            self.client.subscribe(topic)
            print(f"Subscribed to topic: {topic}")

    def print_loaded_topics(self):
        for topic, table_name in self.topics.items():
            print(f"Topic: {topic} -> Table: {table_name}")

    def threshold_exceeded_notification(self, payload):
        self.client.publish("alert/testing", payload)
        print("LED state changed: ", payload)
