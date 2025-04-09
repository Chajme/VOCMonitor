import threading

from flask import Flask
from flask_mail import Mail
from flask_socketio import SocketIO

from app import Config
from app.notification_manager import NotificationManager
from database.db_manager import DatabaseManager
from mqtt_manager import MQTTManager


class VOCMonitor:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config.from_object(Config)

        self.socketio = SocketIO(self.app, async_mode="gevent")
        self.mail = Mail(self.app)

        self.db = DatabaseManager()
        self.notification_manager = NotificationManager(
            self.app, self.socketio, self.mail, self.db
        )
        self.mqtt_manager = MQTTManager(self.db, self.notification_manager)

    def initialize_app(self):
        self.db.initialize_db()
        self.db.new_device("esp", "data")
        self.db.new_device("device", "new/topic")
        self.db.clear_table("esp")
        self.db.clear_table("device")

        self.db.set_selected_device("esp")

        from app.routes import Routes

        routes = Routes(
            self.db,
            self.mqtt_manager,
            self.notification_manager,
            self.socketio,
            self.mail,
        )
        self.app.register_blueprint(routes.routes)
        routes.register_socket_events()

    def run(self):
        # Start MQTT before creating Flask app
        mqtt_thread = threading.Thread(target=self.mqtt_manager.run_mqtt, daemon=True)
        mqtt_thread.start()

        # Create Flask app and Socket.IO
        self.initialize_app()
        self.socketio.init_app(self.app, async_mode="gevent")

        print("Starting production server on port 8000...")
        """eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 8000)), app)"""

        try:
            self.socketio.run(self.app, debug=True, use_reloader=False)
        except KeyboardInterrupt:
            print("Stopping the server...")
            self.socketio.stop()
