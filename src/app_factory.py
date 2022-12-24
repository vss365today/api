import json
from importlib import import_module

import sys_vars
from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from werkzeug.exceptions import HTTPException

import src.configuration as config
from src.blueprints import all_blueprints, v2_blueprints
from src.core import logger
from src.core.database import models
from src.core.database.core import get_db_conn_uri
from src.core.helpers.JsonEncode import JsonEncode


def create_app():
    """Create an instance of the app."""
    app = Flask(__name__)

    # Override the default JSON encoder with a customized one
    app.json_encoder = JsonEncode

    # Load the app configuration
    app.config.update(config.get_app_config("default"))
    app.config.update(config.get_app_config(app.config["ENV"]))
    app.config.update(config.get_secrets_list(app.config["ENV"]))

    # Put the app secret key into the expected key
    app.config["SECRET_KEY"] = sys_vars.get("SECRET_KEY_API")

    # Load any extensions
    CORS(app)
    api = Api(app)

    # Create a database connection
    with app.app_context():
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = get_db_conn_uri()
        models.db.init_app(app)

    # Add a file logger to record errors
    app.logger.addHandler(logger.file_handler(app.config["LOG_PATH"]))

    # Register the resources
    for bp in all_blueprints:
        import_module(bp.import_name)
        app.register_blueprint(bp)

    # Register the v2 endpoints
    # TODO Change the name back to import_name after v1 is gone
    for bp in v2_blueprints:
        import_module(bp.import_name)
        api.register_blueprint(bp, name=f"v2.{bp.import_name}")

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
