from mqtt_manager import MQTTManager
from server.web_server import WebServer
import threading

mqtt_manager = MQTTManager()
mqtt_thread = threading.Thread(target=mqtt_manager.run_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

web_server = WebServer(mqtt_manager)
