import json
from importlib import import_module
from os import getenv

import sys_vars
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from flask_smorest import Api
from werkzeug.exceptions import HTTPException

import src.configuration as config
from src.blueprints import all_blueprints, v2_blueprints
from src.core import logger, json_special
from src.core.database import models


# Modify Flask's JSON encoder to stringify some datatypes how I want
DefaultJSONProvider.default = staticmethod(json_special.json_output)


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

    # Register the resources
    for bp in all_blueprints:
        import_module(bp.import_name)
        app.register_blueprint(bp)

    # Register the v2 endpoints
    for bp in v2_blueprints:
        import_module(bp.import_name)
        api.register_blueprint(bp, name=bp.name.title())

    # TODO Remove this with v1 removal
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Return JSON instead of HTML for API errors.
        Copied from
        https://flask.palletsprojects.com/en/1.1.x/errorhandling/#generic-exception-handlers
        """
        # Start with the correct headers and status code from the error
        response = e.get_response()

        # Replace the body with JSON
        response.data = json.dumps(
            {"code": e.code, "name": e.name, "description": e.description}
        )
        response.content_type = "application/json"
        return response

    return app
