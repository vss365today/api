from contextlib import contextmanager
from typing import Any, Generator

from flask_quick_sql import QuickSQL
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.sql import text

from src.core.database.models import db


__all__ = ["connect_to_db", "quick_sql"]


quick_sql = QuickSQL()


class _Result:
    """Wrapper class for a raw SQL query result."""

    def __init__(self, /, result: CursorResult) -> None:
        self._result: CursorResult = result

    def __iter__(self) -> Generator[dict[str, Any], None, None]:
        """Iterate over all results from the query."""
        for r in self.all():
            yield r

    def all(self) -> list[dict[str, Any]]:
        """Fetch all results from the query."""
        return [r._asdict() for r in self._result.all()]

    def first(self) -> dict[str, Any] | None:
        """Fetch the first result from the query."""
        # Specifically handle no results
        if (r := self._result.first()) is None:
            return None
        return r._asdict()

    def one(self) -> dict[str, Any] | None:
        """Fetch the only result from the query."""
        # Specifically handle no results
        if (r := self._result.one_or_none()) is None:
            return None
        return r._asdict()


class _Query:
    """Wrapper class for executing a SQL query."""

    @staticmethod
    def query(sql, /, **kwargs) -> _Result:
        """Execute a SQL query."""
        with db.engine.connect() as conn:
            return _Result(conn.execute(statement=text(sql), parameters=kwargs))


@contextmanager
def connect_to_db() -> Generator[type[_Query], None, None]:
    """Create a connection to the database."""
    yield _Query
