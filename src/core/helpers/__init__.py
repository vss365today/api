from datetime import datetime
from typing import Dict, Tuple

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


def make_response(status: int, data: dict = {}) -> Tuple[dict, int]:
    return (data, status)


def make_error_response(msg: str, status: int) -> Tuple[Dict[str, str], int]:
    return make_response(status, {"error_msg": msg})
