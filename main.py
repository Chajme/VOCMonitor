import threading

import eventlet

from app import create_app
from database.db_manager import DatabaseManager
from mqtt_manager import MQTTManager

# Initialize database and MQTT
db = DatabaseManager()
mqtt_manager = MQTTManager(db)

# Start MQTT in a thread
mqtt_thread = threading.Thread(target=mqtt_manager.run_mqtt, daemon=True)
mqtt_thread.start()

# Create app and socketio and init socketio app
app, socketio = create_app(mqtt_manager, db)
socketio.init_app(app, async_mode="eventlet", ping_interval=25, ping_timeout=60)

# If the main is run and main, start a server on the specified address
if __name__ == "__main__":
    print("Starting production server with eventlet on port 8000...")
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 8000)), app)
