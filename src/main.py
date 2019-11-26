import json
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.exceptions import HTTPException

from src.blueprints import Prompt, Search, Writer
from src.extensions import init_extensions


def create_app():
    app = Flask(__name__)
    # https://stackoverflow.com/a/45333882
    app.wsgi_app = ProxyFix(app.wsgi_app)
    init_extensions(app)

    # Register the resources
    app.register_blueprint(Prompt)
    app.register_blueprint(Search)
    app.register_blueprint(Writer)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Return JSON instead of HTML for API errors.
        Copied from
        https://flask.palletsprojects.com/en/1.1.x/errorhandling/#generic-exception-handlers
        """
        # start with the correct headers and status code from the error
        response = e.get_response()

        # replace the body with JSON
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description
        })
        response.content_type = "application/json"
        return response

    return app
