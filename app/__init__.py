"""Initializes a development server for debugging purposes."""

import threading

from flask import Flask
from flask_mail import Mail
from flask_socketio import SocketIO

from app.config import Config
from app.notification_manager import NotificationManager
from database.db_manager import DatabaseManager
from mqtt_manager import MQTTManager


def create_app(db_manager):
    """Creates the app and socketio, initialized db, routes and notifications and returns app and socketio."""

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initializes Socket.IO with threading
    socketio = SocketIO(app, async_mode="threading")
    mail = Mail(app)

    notif_manager = NotificationManager(app, socketio, mail, db_manager)

    mqtt_manager = MQTTManager(db_manager, notif_manager)
    mqtt_thread = threading.Thread(target=mqtt_manager.run_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # Initializes the db
    db_manager.initialize_db()
    db_manager.new_device("esp", "data")
    db_manager.new_device("device", "new/topic")
    db_manager.clear_table("esp")
    db_manager.clear_table("device")

    from app.routes import Routes

    # Initializes routes and registers them
    routes = Routes(db_manager, mqtt_manager, notif_manager, socketio)
    app.register_blueprint(routes.routes)

    # Registers socket events
    notif_manager.register_socket_events()

    return app, socketio


if __name__ == "__main__":
    # Initializes a db and creates the app
    db = DatabaseManager()
    flask_app, socketio_t = create_app(db)

    try:
        # Runs the development web server
        socketio_t.run(
            flask_app, debug=True, use_reloader=False, allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("Stopping the server...")
        socketio_t.stop()
