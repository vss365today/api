import json
from importlib import import_module

from flask import Flask
from flask_cors import CORS

# from flask_smorest import Api
from werkzeug.exceptions import HTTPException

import src.configuration as config
from src.blueprints import all_blueprints
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

    # Put the app secret key into the expected key
    app.config["SECRET_KEY"] = app.config["SECRET_KEY_API"]
    del app.config["SECRET_KEY_API"]

    # Load any extensions
    CORS().init_app(app)

    # Create a database connection
    with app.app_context():
        app.config["SQLALCHEMY_DATABASE_URI"] = get_db_conn_uri()
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        # models.db.init_app(app)

        # Create the database tables if needed
        # if not models.db.engine.table_names():
        #     models.db.create_all()

        # Sometimes, the triggers don't get created
        # This sees to make them be consistently created
        # for trigger in models.ALL_TRIGGERS:
        #     models.db.session.execute(trigger)

    # Init API use handling
    # api = Api(app)

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
        # Start with the correct headers and status code from the error
        response = e.get_response()

        # Replace the body with JSON
        response.data = json.dumps(
            {"code": e.code, "name": e.name, "description": e.description}
        )
        response.content_type = "application/json"
        return response

    return app
