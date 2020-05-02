from flask_cors import CORS


def init_extensions(app):
    """Init any Flask extensions."""
    CORS().init_app(app)
