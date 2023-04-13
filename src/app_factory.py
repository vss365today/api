from importlib import import_module
from os import getenv

import sys_vars
from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

import src.configuration as config
from src.core import logger
from src.core.database import models
from src.views import v2_blueprints


def create_app() -> Flask:
    """Create an instance of the app."""
    app = Flask(__name__)

    # Load the app configuration
    app.config.update(config.get_app_config("default"))
    app.config.update(config.get_app_config(getenv("FLASK_ENV")))
    app.config.update(config.get_secrets_list(getenv("FLASK_ENV")))

    # Put the app secret key into the expected key
    app.config["SECRET_KEY"] = sys_vars.get("SECRET_KEY_API")

    # Load any extensions
    CORS(app)
    api = Api(app)

    # Create a database connection
    with app.app_context():
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://{}:{}@{}/{}".format(
            config.get_secret("DB_USERNAME"),
            config.get_secret("DB_PASSWORD"),
            app.config["DB_HOST"],
            app.config["DB_DBNAME"],
        )
        models.db.init_app(app)

    # Add a file logger to record errors
    app.logger.addHandler(logger.file_handler(app.config["LOG_PATH"]))

    # Register the v2 endpoints
    for bp in v2_blueprints:
        import_module(bp.import_name)
        api.register_blueprint(bp, name=bp.name.title())

    return app
