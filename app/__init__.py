
import os
from flask import Flask
from flask_mysqldb import MySQL
from config import Config

mysql = MySQL()


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    app.config.from_object(Config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY is missing from environment configuration.")

    mysql.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    return app
