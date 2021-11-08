import records
from flask import current_app


__all__ = ["connect_to_db", "flatten_records"]


def connect_to_db() -> records.Database:
    """Create a connection to the database."""
    conn_str = "mysql://{}:{}@{}/{}".format(
        current_app.config["DB_USERNAME"],
        current_app.config["DB_PASSWORD"],
        current_app.config["DB_HOST"],
        current_app.config["DB_DBNAME"],
    )
    return records.Database(conn_str).get_connection()


def flatten_records(tup: tuple) -> list:
    """Flatten a nested list of records."""
    return [item[0] for item in tup]
