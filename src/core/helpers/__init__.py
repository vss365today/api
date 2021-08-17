from datetime import date, datetime
from flask import current_app
from typing import Any, Dict, Tuple, Union

import tweepy


__all__ = [
    "twitter_v2_api",
    "format_datetime_pretty",
    "format_datetime_ymd",
    "make_response",
    "make_error_response",
]


def twitter_v2_api() -> tweepy.Client:
    """Connect to Twitter API v2 using a Bearer token."""
    return tweepy.Client(bearer_token=current_app.config["TWITTER_BEARER"])


def format_datetime_pretty(date_obj: Union[date, datetime]) -> str:
    """Pretty format a date as MM DD, YYYY."""
    return date_obj.strftime("%B %d, %Y")


def format_datetime_ymd(date_obj: Union[date, datetime]) -> str:
    """Format a date as YYYY-MM-DD."""
    return date_obj.strftime("%Y-%m-%d")


def make_response(status: int, data: Dict[str, Any] = None) -> Tuple[dict, int]:
    """Construct a non-error endpoint response."""
    if data is None:
        data = {}
    return (data, status)


def make_error_response(status: int, msg: str) -> Tuple[Dict[str, str], int]:
    """Construct an error endpoint response."""
    return make_response(status, {"error_msg": msg})
