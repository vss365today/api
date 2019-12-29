from flask_cors import CORS

from src.core.config import load_app_config


def init_extensions(app):
    CORS().init_app(app)
    app.config.update(load_app_config())
