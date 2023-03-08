import records
from flask import current_app

from src.configuration import get_secret


__all__ = ["connect_to_db", "get_db_conn_uri"]


def get_db_conn_uri() -> str:
    """Create a database connection URI."""
    return "mysql+pymysql://{}:{}@{}/{}".format(
        get_secret("DB_USERNAME"),
        get_secret("DB_PASSWORD"),
        current_app.config["DB_HOST"],
        current_app.config["DB_DBNAME"],
    )


def connect_to_db() -> records.Database:
    """Create a connection to the database."""
    return records.Database(get_db_conn_uri()).get_connection()
