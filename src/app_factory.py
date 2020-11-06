from importlib import import_module
import json

from flask import Flask
from werkzeug.exceptions import HTTPException

import src.configuration as config
from src.blueprints import all_blueprints
from src.extensions import init_extensions


def create_app():
    """Create an instance of the app."""
    app = Flask(__name__)

    # Load the app configuration
    app.config.update(config.get_app_config("default"))
    app.config.update(config.get_app_config(app.config["ENV"]))

    # Put the app secret key into the expected key
    app.config["SECRET_KEY"] = app.config["SECRET_KEY_API"]
    del app.config["SECRET_KEY_API"]

    # Load the extensions
    init_extensions(app)

    # Register the resources
    for bp in all_blueprints:
        import_module(bp.import_name)
        app.register_blueprint(bp)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Return JSON instead of HTML for API errors.
        Copied from
        https://flask.palletsprojects.com/en/1.1.x/errorhandling/#generic-exception-handlers
        """
        # start with the correct headers and status code from the error
        response = e.get_response()

        # replace the body with JSON
        response.data = json.dumps(
            {"code": e.code, "name": e.name, "description": e.description}
        )
        response.content_type = "application/json"
        return response

    return app
