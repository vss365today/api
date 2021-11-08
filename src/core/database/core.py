import records
from flask import current_app


__all__ = ["connect_to_db", "flatten_records", "get_db_conn_uri"]


def get_db_conn_uri() -> str:
    """Create a database connection URI."""
    return "mysql://{}:{}@{}/{}".format(
        current_app.config["DB_USERNAME"],
        current_app.config["DB_PASSWORD"],
        current_app.config["DB_HOST"],
        current_app.config["DB_DBNAME"],
    )


def connect_to_db() -> records.Database:
    """Create a connection to the database."""
    return records.Database(get_db_conn_uri()).get_connection()


def flatten_records(tup: tuple) -> list:
    """Flatten a nested list of records."""
    return [item[0] for item in tup]
