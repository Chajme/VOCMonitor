"""Main class that runs the whole app and starts a web server in production version."""

import socket
import threading

from flask import Flask
from flask_mail import Mail
from flask_socketio import SocketIO

from app import Config
from app.notification_manager import NotificationManager
from app.routes import Routes
from database.db_manager import DatabaseManager
from mqtt_manager import MQTTManager


class VOCMonitor:
    """Class represents our whole system."""

    def __init__(self):
        """Initializes app, sets it's config, initializes socketio, mail, db, mqtt_manager and notification_manager."""

        self.app = Flask(__name__)
        self.app.config.from_object(Config)

        self.socketio = SocketIO(self.app, async_mode="gevent")
        self.mail = Mail(self.app)

        self.db = DatabaseManager()
        self.notification_manager = NotificationManager(
            self.app, self.socketio, self.mail, self.db
        )
        self.mqtt_manager = MQTTManager(self.db, self.notification_manager)

        self.routes = Routes(
            self.db, self.mqtt_manager, self.notification_manager, self.mail
        )

        self.socketio.init_app(self.app)

        self.app.register_blueprint(self.routes.routes)
        self.notification_manager.register_socket_events()

    def initialize_app(self):
        """Initializes apps db, adds default devices and sets the currently selected device to one of them."""

        self.db.initialize_db()
        self.db.set_selected_device("esp")

        # self.db.new_device("esp", "data")
        # self.db.new_device("device", "new/topic")
        # self.db.clear_table("esp")
        # self.db.clear_table("device")

    def run(self):
        """Stars the mqtt_manager in a thread and starts the production web server on port 8000."""

        # Start MQTT before creating Flask app
        mqtt_thread = threading.Thread(target=self.mqtt_manager.run_mqtt, daemon=True)
        mqtt_thread.start()

        # Create Flask app and Socket.IO
        self.initialize_app()

        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        try:
            print(">>> Starting production server on port 8000...")
            print(">>> Localhost:   http://localhost:8000")
            print(f">>> LAN:   http://{local_ip}:8000")
            self.socketio.run(self.app, host="0.0.0.0", port=8000)
        except KeyboardInterrupt:
            print("Stopping the server...")
            self.socketio.stop()
