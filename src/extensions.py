from src.core.config import load_app_config
from src.core.database import create_new_database

from flask_jwt_extended import JWTManager


def init_extensions(app):
    # Load app extensions
    app.config.update(load_app_config())
    JWTManager(app)

    # If a database is needed, one will be made
    create_new_database()
