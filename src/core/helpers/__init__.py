from datetime import datetime
from typing import Any, Dict, Tuple

from flask import jsonify

__all__ = [
    "format_datetime_iso",
    "format_datetime_pretty",
    "make_response",
    "make_error_response",
]


def format_datetime_iso(date_obj: datetime) -> str:
    """Format a date as YYYY-MM-DD."""
    return date_obj.strftime("%Y-%m-%d")


def format_datetime_pretty(date_obj: datetime) -> str:
    """Pretty format a date as MM DD, YYYY."""
    return date_obj.strftime("%B %d, %Y")


def make_response(status: int, data: Any = None) -> Tuple[dict, int]:
    """Construct a non-error endpoint response."""
    if data is None:
        data = {}
    return (jsonify(data), status)


def make_error_response(status: int, msg: str) -> Tuple[Dict[str, str], int]:
    """Construct an error endpoint response."""
    return make_response(status, {"error_msg": msg})
