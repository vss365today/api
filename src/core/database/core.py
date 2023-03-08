from contextlib import contextmanager
from typing import Any, Generator

import records
from flask import current_app
from sqlalchemy.engine.result import ResultProxy, RowProxy
from sqlalchemy.sql import text

from src.configuration import get_secret
from src.core.database.models import db


__all__ = ["connect_to_db", "connect_to_db2", "get_db_conn_uri"]


class _Result:
    """Wrapper class for a raw SQL query result."""

    def __init__(self, /, result: ResultProxy) -> None:
        self._result: ResultProxy = result

    def __iter__(self) -> Generator[dict[str, Any], None, None]:
        """Iterate over all results from the query."""
        for r in self.all():
            yield r

    def _to_dict(self, /, r: RowProxy) -> dict[str, Any]:
        return dict(zip(r.keys(), r.values(), strict=True))

    def all(self) -> list[dict[str, Any]]:
        """Fetch all results from the query."""
        return [self._to_dict(r) for r in self._result.fetchall()]

    def first(self) -> dict[str, Any] | None:
        """Fetch the first result from the query."""
        # Specifically handle no results
        if (r := self._result.first()) is None:
            return None
        return self._to_dict(r)

    def one(self) -> dict[str, Any] | None:
        """Fetch the only result from the query."""
        # Specifically handle no results
        if (r := self._result.fetchone()) is None:
            return None
        return self._to_dict(r)


class _Query:
    """Wrapper class for executing a SQL query."""

    @staticmethod
    def query(sql, /, **kwargs) -> _Result:
        """Execute a SQL query."""
        with db.engine.connect() as conn:
            return _Result(conn.execute(text(sql), **kwargs))


@contextmanager
def connect_to_db2() -> Generator[type[_Query], None, None]:
    """Create a connection to the database."""
    yield _Query


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
