import threading

from flask import Flask
from flask_mail import Mail
from flask_socketio import SocketIO

from app.config import Config
from database.db_manager import DatabaseManager
from mqtt_manager import MQTTManager


def create_app(mqtt, db_manager):
    app = Flask(__name__)
    app.config.from_object(Config)

    socketio = SocketIO(app, async_mode="threading")
    mail = Mail(app)

    db_manager = db_manager
    db_manager.initialize_db()

    db_manager.new_device("esp", "data")
    db_manager.new_device("device", "new/topic")

    from app.routes import Routes

    routes = Routes(db_manager, mqtt, socketio, mail)
    app.register_blueprint(routes.routes)
    routes.register_socket_events()

    return app, socketio


if __name__ == "__main__":
    db = DatabaseManager()
    mqtt_manager = MQTTManager(db)
    mqtt_thread = threading.Thread(target=mqtt_manager.run_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    flask_app, socketio_t = create_app(mqtt_manager, db)
    flask_app.run()
