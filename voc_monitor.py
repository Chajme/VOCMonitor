import threading

import eventlet

from app import create_app
from database.db_manager import DatabaseManager
from mqtt_manager import MQTTManager


class VOCMonitor:
    def __init__(self):
        self.db = DatabaseManager()
        self.mqtt_manager = MQTTManager(self.db)

    def run(self):
        # Start MQTT before creating Flask app
        mqtt_thread = threading.Thread(target=self.mqtt_manager.run_mqtt, daemon=True)
        mqtt_thread.start()

        # Create Flask app and Socket.IO
        app, socketio = create_app(self.mqtt_manager, self.db)
        socketio.init_app(app, async_mode="eventlet")

        print("Starting production server on port 8000...")
        eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 8000)), app)
