from datetime import date, datetime
from typing import Any

import tweepy

from src.configuration import get_secret


__all__ = [
    "twitter_v2_api",
    "format_datetime_pretty",
    "format_datetime_ymd",
    "make_response",
    "make_error_response",
]


def twitter_v2_api() -> tweepy.Client:
    """Connect to Twitter API v2 using a Bearer token."""
    return tweepy.Client(bearer_token=get_secret("TWITTER_BEARER"))


def format_datetime_pretty(date_obj: date | datetime) -> str:
    """Pretty format a date as MM DD, YYYY."""
    return date_obj.strftime("%B %d, %Y")


def format_datetime_ymd(date_obj: date | datetime) -> str:
    """Format a date as YYYY-MM-DD."""
    return date_obj.strftime("%Y-%m-%d")


def make_response(
    status: int, data: dict[str, Any] | None = None
) -> tuple[dict[str, Any], int]:
    """Construct a non-error endpoint response."""
    if data is None:
        data = {}
    return (data, status)


def make_error_response(status: int, msg: str) -> tuple[dict[str, str], int]:
    """Construct an error endpoint response."""
    return make_response(status, {"error_msg": msg})
