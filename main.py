import threading

from app import create_app
from mqtt_manager import MQTTManager

mqtt_manager = MQTTManager()
mqtt_thread = threading.Thread(target=mqtt_manager.run_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

app = create_app(mqtt_manager)
app.run()
