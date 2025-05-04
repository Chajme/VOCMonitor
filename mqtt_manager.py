"""Module handles the mqtt connections."""

import datetime
import time

import paho.mqtt.client as mqtt


class MQTTManager:
    """Represents a manager for mqtt connections with the server."""

    def __init__(self, db, notification_manager, mqtt_server, mqtt_port):
        """Receives db as a parameter, sets the server ip, port and selected device. Creates a client."""

        self.server = mqtt_server
        self.port = mqtt_port
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="pc", protocol=mqtt.MQTTv5
        )

        self.db_manager = db
        self.notification_manager = notification_manager

        self.topics = {}
        self.voc_index = {}

        self.threshold_exceeded = False
        self.last_alarm_state = None

    def on_connect(self, client, userdata, flags, reason_code, properties):
        """Callback function to handle connecting to mqtt broker. Once connected loads topics and subscribes."""

        if reason_code == 0:
            self.load_topics_from_db()
            self.print_loaded_topics()
            self.subscribe_to_all_topics()
        else:
            print(f">>> Connection error: {str(reason_code)}")

    def on_message(self, client, userdata, message):
        """Callback function handles oncoming messages. Every 5 messages saves an average of voc to the db."""

        # Splits the received message based on the commas
        msg_str = str(message.payload.decode())
        msg_split = msg_str.split(",")

        # If the message isn't in the correct format (correct length) do nothing
        if len(msg_split) < 3:
            print(f">>> Invalid message received: {msg_str}")
            return

        # Save the parts of the split message to local variables
        temperature, humidity, voc = msg_split[0], msg_split[1], msg_split[2]

        # If the messages topic was received and the topic is in saved topics
        if message.topic in self.topics:
            table_name = self.topics[message.topic]

            # Save the received voc to the correct voc index array
            self.voc_index[table_name].append(int(voc))
            curr_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.esp_notif_alarm(int(voc), table_name)

            # If the voc index array with the specified table_name has 5 elements
            if len(self.voc_index[table_name]) == 5:
                # Calculate an average voc for the 5 values
                avg_voc = int(
                    sum(self.voc_index[table_name]) / len(self.voc_index[table_name])
                )
                # Insert the data into the db
                self.db_manager.insert(
                    table_name, curr_time, temperature, humidity, avg_voc
                )

                self.notification_manager.check_email_notif(avg_voc, table_name)

                # Clear the voc array of the specified table
                self.voc_index[table_name].clear()
                print(f"{table_name}: {self.db_manager.get_last_row(table_name)}")

    def run_mqtt(self):
        """Function to handle the mqtt connection"""

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        result = None

        # Retry connection until the connection is established, retry every 15 seconds
        while result is None or result != 0:
            try:
                result = self.client.connect(self.server, self.port, 60)
            except Exception as e:
                print(f">>> Connection failed: {e}")
                print(">>> Will try reconnecting in 15 seconds...")
            time.sleep(15)

        try:
            self.client.loop_start()
        except KeyboardInterrupt:
            self.client.disconnect()

    def subscribe(self, topic, device_name):
        """Subscribe to a specified topic and add the topic to an array with the specified device_name."""

        if topic not in self.topics:
            self.topics[topic] = device_name
            self.voc_index[device_name] = []
            self.client.subscribe(topic)
        print(f">>> Subscribed to new topic: {topic}, Table: {device_name}")

    def unsubscribe(self, topic):
        """Unsubscribe from the specified topic."""

        if topic in self.topics:
            table_name = self.topics[topic]
            self.client.unsubscribe(topic)

            del self.topics[topic]
            del self.voc_index[table_name]
            print(f">>> Unsubscribed from topic: {topic}, Removed table: {table_name}")

    def load_topics_from_db(self):
        """Load all the topics from the db into an array."""

        rows = self.db_manager.get_device_topics()
        for topic, device_name in rows:
            self.topics[topic] = device_name
            self.voc_index[device_name] = []
        print(">>> Loaded topics: ", self.topics)

    def clear_topics(self):
        """Clear all topics in the array."""

        self.topics.clear()
        self.print_loaded_topics()

    def subscribe_to_all_topics(self):
        """Subscribe to all topics in the array."""

        for topic in self.topics.keys():
            self.client.subscribe(topic)
            print(f">>> Subscribed to topic: {topic}")

    def print_loaded_topics(self):
        """Print all the loaded topics."""

        for topic, table_name in self.topics.items():
            print(f">>> Topic: {topic} -> Table: {table_name}")

    def threshold_exceeded_notification(self, payload):
        """Send a message to the specified topic with the payload."""

        self.client.publish("alert/testing", payload)
        print(">>> LED state changed: ", payload)

    def esp_notif_alarm(self, voc, device):
        """Sends a message to the esp based on a boolean returned by NotificationManager"""

        if self.notification_manager.is_esp_alarm_enabled():
            current_state = self.notification_manager.send_esp_alarm_notif(voc, device)
            if current_state != self.last_alarm_state:
                if current_state:
                    self.threshold_exceeded_notification("on")
                else:
                    self.threshold_exceeded_notification("off")
            self.last_alarm_state = current_state
