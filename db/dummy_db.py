import json
import sys
from os import environ
from pathlib import Path

from flask import Flask

# We have to add the app path to the path to get the db schema
APP_ROOT = Path(__file__).parent.parent
sys.path.insert(0, APP_ROOT.as_posix())

from src.core.database import models


def get_config(file: str) -> str:
    return json.loads((APP_ROOT / "configuration" / file).read_text())


def get_secret(key: str) -> str:
    if "SYS_VARS_PATH" in environ:
        f = (Path(environ["SYS_VARS_PATH"]) / key).resolve()
    else:
        f = (APP_ROOT / ".." / "secrets" / key).resolve()
    return f.read_text().strip()


def create_app():
    """Dummy Flask instance used for database management."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret tunnel"
    db_name = get_config("default.json")["appConfig"]["DB_DBNAME"]

    with app.app_context():
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://{}:{}@{}/{}".format(
            get_secret("DB_USERNAME"),
            get_secret("DB_PASSWORD"),
            get_secret("DB_HOST"),
            db_name,
        )
        models.db.init_app(app)
    return app
