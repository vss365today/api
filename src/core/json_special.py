from datetime import date, datetime
from typing import Any

from flask.json.provider import _default


__all__ = ["json_output"]


def json_output(o: Any) -> Any:
    """Format dates and datetimes in ISO 8601 for JSON."""
    # TODO: Remove this with v1 removal. v2 handles this correctly already
    if isinstance(o, datetime):
        return o.isoformat()

    if isinstance(o, date):
        return o.isoformat()

    return _default(o)
