import records
from flask import current_app


__all__ = ["connect_to_db", "create_transaction", "flatten_records"]


def connect_to_db() -> records.Database:
    """Create a connection to the database."""
    conn_str = "mysql+pymysql://{}:{}@{}/{}".format(
        current_app.config["DB_USERNAME"],
        current_app.config["DB_PASSWORD"],
        current_app.config["DB_HOST"],
        current_app.config["DB_DBNAME"],
    )
    conn = records.Database(conn_str)
    return conn


def create_transaction(db):
    """Reach into SQLAlchemy to start a transaction."""
    return db._engine.begin()  # skipcq: PYL-W0212


def flatten_records(tup: tuple) -> list:
    """Flatten a nested list of records."""
    return [item[0] for item in tup]
