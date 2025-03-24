import threading

from flask import Flask
from flask_mail import Mail
from flask_socketio import SocketIO

from app.config import Config
from database.db_manager import DatabaseManager
from mqtt_manager import MQTTManager


def create_app(mqtt):
    app = Flask(__name__)
    app.config.from_object(Config)

    mail = Mail(app)
    socketio = SocketIO(app)

    db = DatabaseManager()
    db.initialize_db()

    db.new_device("esp", "data")
    db.new_device("device", "new/topic")

    from app.routes import Routes

    routes = Routes(db, mqtt, socketio, mail)
    app.register_blueprint(routes.routes)
    routes.register_socket_events()

    return app


if __name__ == "__main__":
    mqtt_manager = MQTTManager()
    mqtt_thread = threading.Thread(target=mqtt_manager.run_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    app = create_app(mqtt_manager)
    app.run()
